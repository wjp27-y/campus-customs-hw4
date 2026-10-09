"""Campus Customs API.

Run from this folder with:
    uvicorn main:app --reload --port 8000
"""

import json
import logging
import os
import sqlite3
import time
from collections import defaultdict, deque
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv

# Load API keys (e.g. ANTHROPIC_API_KEY) from backend/.env before the agent is imported.
load_dotenv(Path(__file__).parent / ".env")

from fastapi import Cookie, FastAPI, HTTPException, Request, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic_ai.exceptions import AgentRunError, ModelAPIError  # noqa: E402

from agent import (  # noqa: E402
    check_reply,
    local_fact_checker,
    local_model,
    missing_api_key,
    pick_model,
    product_ids_in,
    run_chat,
)
from auth import current_user, init_auth_tables, make_router  # noqa: E402
from models import MAX_HISTORY_MESSAGES, AgentDeps, ChatHistoryMessage, ChatRequest, ChatResponse, cap_reply  # noqa: E402
from tools import build_facts, build_shopper_context, load_product_cards, similar_products  # noqa: E402

log = logging.getLogger("campus_customs")
# Print this app's INFO logs (which model answered, fact-check corrections) next to uvicorn's.
log.setLevel(logging.INFO)
if not log.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:     %(name)s: %(message)s"))
    log.addHandler(_handler)

# data/ lives at the root of the hw 4 folder (shared by every problem).
DATA_DIR = Path(os.environ.get("CC_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
DB_PATH = DATA_DIR / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product photos: catalogue.image_file_path is "products/<file>.jpg", relative to DATA_DIR.
# Mount only the products folder so the database file itself is never downloadable.
app.mount("/images/products", StaticFiles(directory=DATA_DIR / "products"), name="images")


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """Open a connection; commit on success, roll back on error, always close."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def product_from_row(row: sqlite3.Row) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_url": f"/images/{row['image_file_path']}",
        "price": row["price"],
    }


with get_db() as _conn:
    init_auth_tables(_conn)
    # Customer memory (Problem 8): keep the page context of each saved user message.
    if "page_context_json" not in {r["name"] for r in _conn.execute("PRAGMA table_info(chat_messages)")}:
        _conn.execute("ALTER TABLE chat_messages ADD COLUMN page_context_json TEXT")

app.include_router(make_router(get_db))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def list_products() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        stock = dict(
            conn.execute("SELECT product_id, SUM(quantity) FROM inventory GROUP BY product_id").fetchall()
        )
    return [{**product_from_row(r), "in_stock": (stock.get(r["product_id"]) or 0) > 0} for r in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        inv = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()
    sizes = sorted(
        ({"size": r["size"], "quantity": r["quantity"], "in_stock": r["quantity"] > 0} for r in inv),
        key=lambda s: SIZE_ORDER.index(s["size"]) if s["size"] in SIZE_ORDER else len(SIZE_ORDER),
    )
    return {**product_from_row(row), "sizes": sizes, "in_stock": any(s["in_stock"] for s in sizes)}


# ---------------------------------------------------------------- chat

CHAT_RATE_LIMIT = 20  # messages per minute per IP, to cap model cost and abuse
_chat_requests: dict[str, deque[float]] = defaultdict(deque)


def _check_chat_rate(ip: str) -> None:
    now = time.monotonic()
    recent = _chat_requests[ip]
    while recent and recent[0] < now - 60:
        recent.popleft()
    if len(recent) >= CHAT_RATE_LIMIT:
        raise HTTPException(429, "You're sending messages too quickly. Please wait a moment and try again.")
    recent.append(now)


def _stored_product_ids(products_json: str | None) -> list[str]:
    if not products_json:
        return []
    try:
        return [p["product_id"] for p in json.loads(products_json) if isinstance(p, dict) and "product_id" in p]
    except (ValueError, TypeError):
        return []


def _load_history(conn: sqlite3.Connection, user_id: int, limit: int) -> list[sqlite3.Row]:
    rows = conn.execute(
        "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    return list(reversed(rows))


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    _check_chat_rate(request.client.host if request.client else "")
    message = req.message.strip()
    if not message:
        raise HTTPException(400, "Message can't be empty.")

    # Customer memory: logged-in shoppers' history is loaded from chat_messages; guests' isn't remembered.
    # Both get the page context (validated against the catalogue) and, if logged in, their profile.
    with get_db() as conn:
        user = current_user(conn, cc_session)
        history = []
        if user:
            history = [
                ChatHistoryMessage(role=r["role"], content=r["content"])
                for r in _load_history(conn, user["id"], MAX_HISTORY_MESSAGES)
                if r["role"] in ("user", "assistant")
            ]
        shopper = build_shopper_context(conn, user, req.page_context)

    deps = AgentDeps(get_db=get_db, shopper=shopper)
    # Every chat is answered by the PydanticAI agent. With no LLM key configured, the agent runs on the
    # local rule-based model (agent.local_model) instead of Claude; tools and output validation are the same.
    # Otherwise the cheaper default model answers, and turns that lean on the saved conversation go to the
    # escalation model (agent.pick_model).
    offline = missing_api_key() is not None
    model, model_name = (local_model, "local") if offline else pick_model(message, history, deps)
    log.info("Chat turn on %s (%d history messages)", model_name, len(history))
    try:
        output, turn_messages = await run_chat(message, history, deps, model=model, model_name=model_name)
    except (AgentRunError, ModelAPIError):
        log.exception("Agent run failed")
        raise HTTPException(502, "Sorry, the assistant ran into a problem. Please try again in a moment.")

    # Fact-check prices and stock in the reply against the database (agent.check_reply). If the checker itself
    # fails, the reply is kept: the cards under it are always built from the database anyway.
    reply = output.reply
    with get_db() as conn:
        facts = build_facts(conn, [*output.product_ids, *product_ids_in(turn_messages)])
    try:
        reply, verdict = await check_reply(reply, facts, model=local_fact_checker if offline else None)
        if verdict and not verdict.accurate:
            log.warning("Fact-checker corrected the reply: %s", "; ".join(verdict.problems))
    except (AgentRunError, ModelAPIError):
        log.exception("Fact-check failed; keeping the original reply")
    reply = cap_reply(reply)  # a corrected reply gets the same one-paragraph, 7-sentence cap

    with get_db() as conn:
        # Cards are built from the database, so prices/stock shown are always real even if the model erred.
        cards = load_product_cards(conn, output.product_ids)
        similar = similar_products(conn, cards, output.similar_search)
        if user:
            conn.execute(
                "INSERT INTO chat_messages (user_id, role, content, page_context_json) VALUES (?, 'user', ?, ?)",
                (user["id"], message, shopper.page.model_dump_json(exclude={"last_discussed_product"})),
            )
            conn.execute(
                "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
                (user["id"], reply, json.dumps([c.model_dump() for c in cards]) if cards else None),
            )
    # The structured product matches go back with a heading, so the website can show them as cards on the page.
    title = (output.results_title or "Products from your chat") if cards else None
    return ChatResponse(reply=reply, products=cards, results_title=title, similar=similar)


@app.get("/api/chat/history")
def chat_history(cc_session: str | None = Cookie(default=None)) -> list[dict]:
    """A logged-in shopper's saved conversation, so the widget can restore it."""
    with get_db() as conn:
        user = current_user(conn, cc_session)
        if user is None:
            return []
        rows = _load_history(conn, user["id"], 50)
        return [
            {
                "role": r["role"],
                "content": r["content"],
                "products": [c.model_dump() for c in load_product_cards(conn, _stored_product_ids(r["products_json"]))],
            }
            for r in rows
        ]


@app.delete("/api/chat/history", status_code=204)
def clear_chat_history(cc_session: str | None = Cookie(default=None)) -> Response:
    """"Start over" (Problem 9): delete a logged-in shopper's saved conversation. Guests have nothing saved."""
    with get_db() as conn:
        user = current_user(conn, cc_session)
        if user is not None:
            conn.execute("DELETE FROM chat_messages WHERE user_id = ?", (user["id"],))
    return Response(status_code=204)
