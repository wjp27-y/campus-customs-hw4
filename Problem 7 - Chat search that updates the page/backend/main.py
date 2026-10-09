"""Campus Customs API (FastAPI): products, accounts and login, and the chat that runs the agent (agent.py).

Run from this folder (backend/) with:
    uvicorn main:app --reload --port 8000
"""

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import time
from collections import defaultdict, deque
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load API keys (e.g. ANTHROPIC_API_KEY) before the agent is imported: from .env at the repo root (copied from
# .env.example), and from backend/.env if there is one. A variable that is already set is never overwritten.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv(Path(__file__).parent / ".env")

from fastapi import Cookie, FastAPI, HTTPException, Request, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402
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
from models import MAX_HISTORY_MESSAGES, AgentDeps, ChatHistoryMessage, ChatRequest, ChatResponse, cap_reply  # noqa: E402
from tools import build_facts, build_shopper_context, load_product_cards, similar_products  # noqa: E402

log = logging.getLogger("campus_customs")
# Print this app's INFO logs (which model answered, fact-check corrections) next to uvicorn's.
log.setLevel(logging.INFO)
if not log.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:     %(name)s: %(message)s"))
    log.addHandler(_handler)

# data/ (the local-only data pack) lives at the repo root, next to backend/ and frontend/.
DATA_DIR = Path(os.environ.get("CC_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
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


# ---------------------------------------------------------------- accounts and login (Problem 4)

# Account creation, login, and sessions for Campus Customs.
#
# Passwords are never stored. users.password_hash holds a salted PBKDF2-HMAC-SHA256 hash:
#
#     new accounts:      pbkdf2_sha256$<iterations>$<salt hex>$<hash hex>
#     seeded accounts:   pbkdf2_sha256$<salt>$<hash hex>     (iterations = LEGACY_ITERATIONS)
#
# Seeded hashes are upgraded to the new format the next time that user logs in successfully.

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000  # OWASP 2023 recommendation for PBKDF2-HMAC-SHA256
# Iteration count used for the hashes that shipped in campus_customs.db (their format doesn't record it).
LEGACY_ITERATIONS = int(os.environ.get("CC_LEGACY_PBKDF2_ITERATIONS", "120000"))

MIN_PASSWORD = 8
MAX_PASSWORD = 128
MAX_NAME = 50
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SESSION_COOKIE = "cc_session"
SESSION_DAYS = 7
SECURE_COOKIES = os.environ.get("CC_SECURE_COOKIES") == "1"  # set to 1 when served over HTTPS

MAX_FAILED_LOGINS = 5
LOCKOUT_SECONDS = 15 * 60
_failed_logins: dict[tuple[str, str], deque[float]] = defaultdict(deque)


# ---- password hashing

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS).hex()
    return f"{ALGORITHM}${ITERATIONS}${salt}${digest}"


def _parse_hash(stored: str) -> tuple[int, str, str]:
    parts = stored.split("$")
    if parts[0] != ALGORITHM:
        raise ValueError("unsupported hash algorithm")
    if len(parts) == 4:
        return int(parts[1]), parts[2], parts[3]
    if len(parts) == 3:
        return LEGACY_ITERATIONS, parts[1], parts[2]
    raise ValueError("malformed password hash")


def verify_password(password: str, stored: str) -> bool:
    iterations, salt, expected = _parse_hash(stored)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()
    return hmac.compare_digest(digest, expected)  # constant-time comparison


def needs_rehash(stored: str) -> bool:
    return _parse_hash(stored)[0] != ITERATIONS or stored.count("$") != 3


# Checked when the email doesn't exist, so a missing account takes as long as a wrong password.
_DUMMY_HASH = hash_password(secrets.token_hex(16))


# ---- sessions

def init_auth_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )"""
    )


def _token_hash(token: str) -> str:
    # Only a hash of the session token is stored, so a leaked DB can't be used to hijack sessions.
    return hashlib.sha256(token.encode()).hexdigest()


def _utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def start_session(conn: sqlite3.Connection, response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    conn.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (_token_hash(token), user_id, _utc(expires)),
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_DAYS * 24 * 3600,
        httponly=True,  # not readable from JavaScript, so XSS can't steal it
        samesite="lax",  # not sent on cross-site POSTs (CSRF)
        secure=SECURE_COOKIES,
        path="/",
    )


def current_user(conn: sqlite3.Connection, token: str | None) -> sqlite3.Row | None:
    if not token:
        return None
    return conn.execute(
        """SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id
           WHERE s.token_hash = ? AND s.expires_at > datetime('now')""",
        (_token_hash(token),),
    ).fetchone()


def public_user(row: sqlite3.Row) -> dict:
    # Never send password_hash to the browser.
    return {
        "id": row["id"],
        "name": row["name"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
    }


# ---- brute-force throttling

def _recent_failures(key: tuple[str, str]) -> deque[float]:
    attempts = _failed_logins[key]
    cutoff = time.monotonic() - LOCKOUT_SECONDS
    while attempts and attempts[0] < cutoff:
        attempts.popleft()
    return attempts


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


with get_db() as _conn:
    init_auth_tables(_conn)
    # Customer memory (Problem 8): keep the page context of each saved user message.
    if "page_context_json" not in {r["name"] for r in _conn.execute("PRAGMA table_info(chat_messages)")}:
        _conn.execute("ALTER TABLE chat_messages ADD COLUMN page_context_json TEXT")


@app.post("/api/auth/register", status_code=201)
def register(req: RegisterRequest, response: Response) -> dict:
    first, last = req.first_name.strip(), req.last_name.strip()
    email = req.email.strip().lower()
    if not first or not last:
        raise HTTPException(400, "First and last name are required.")
    if len(first) > MAX_NAME or len(last) > MAX_NAME:
        raise HTTPException(400, f"Names must be at most {MAX_NAME} characters.")
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Please enter a valid email address.")
    if not MIN_PASSWORD <= len(req.password) <= MAX_PASSWORD:
        raise HTTPException(400, f"Password must be {MIN_PASSWORD}-{MAX_PASSWORD} characters.")
    if req.password != req.confirm_password:
        raise HTTPException(400, "Passwords don't match.")

    with get_db() as conn:
        if conn.execute("SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone():
            raise HTTPException(409, "An account with that email already exists.")
        cur = conn.execute(
            "INSERT INTO users (name, first_name, last_name, email, password_hash) VALUES (?, ?, ?, ?, ?)",
            (f"{first} {last}", first, last, email, hash_password(req.password)),
        )
        start_session(conn, response, cur.lastrowid)
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return public_user(row)


@app.post("/api/auth/login")
def login(req: LoginRequest, request: Request, response: Response) -> dict:
    email = req.email.strip().lower()
    key = (request.client.host if request.client else "", email)
    if len(_recent_failures(key)) >= MAX_FAILED_LOGINS:
        raise HTTPException(429, "Too many failed attempts. Please wait 15 minutes and try again.")

    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
        ok = verify_password(req.password, row["password_hash"] if row else _DUMMY_HASH) and row is not None
        if not ok:
            _failed_logins[key].append(time.monotonic())
            # Same message whether the email or the password was wrong, so accounts can't be enumerated.
            raise HTTPException(401, "Incorrect email or password.")

        _failed_logins.pop(key, None)
        if needs_rehash(row["password_hash"]):
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(req.password), row["id"])
            )
        start_session(conn, response, row["id"])
    return public_user(row)


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response, cc_session: str | None = Cookie(default=None)) -> None:
    if cc_session:
        with get_db() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(cc_session),))
    response.delete_cookie(SESSION_COOKIE, path="/")


@app.get("/api/auth/me")
def me(cc_session: str | None = Cookie(default=None)) -> dict:
    with get_db() as conn:
        row = current_user(conn, cc_session)
    if row is None:
        raise HTTPException(401, "Not logged in.")
    return public_user(row)


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
