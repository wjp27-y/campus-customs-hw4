"""Copy each problem's files from the runnable app (app/) into its Problem folder.

The app in app/ is the single source of truth: edit code there, then run

    python sync_problem_folders.py

to refresh the copies in each Problem folder, plus its README and (for Problem 2) the schema dump.
Copies keep the same relative path they have in app/ (e.g. Problem 4/backend/auth.py).
"""

import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app"
HARNESS = "../output/harness.md"

# folder -> (title, harness anchor or None, [(app-relative path, what this problem did with it)])
PROBLEMS: dict[str, tuple[str, str | None, list[tuple[str, str]]]] = {
    "Problem 3 - Build the Campus Customs website": (
        "Problem 3 — Build the Campus Customs website",
        None,
        [
            ("frontend/package.json", "React + Vite + TypeScript project and dependencies"),
            ("frontend/index.html", "HTML entry point"),
            ("frontend/vite.config.ts", "Dev server; proxies /api and /images to FastAPI"),
            ("frontend/tsconfig.json", "TypeScript settings"),
            ("frontend/src/main.tsx", "React entry point and router"),
            ("frontend/src/App.tsx", "Routes for every page, plus footer and chat widget"),
            ("frontend/src/index.css", "Site styles (Yale blue theme)"),
            ("frontend/src/api.ts", "Calls to the backend API"),
            ("frontend/src/types.ts", "TypeScript types for products"),
            ("frontend/src/components/NavBar.tsx", "Top navigation bar: Home, Products, About Us, Log in, Create account"),
            ("frontend/src/components/ProductCard.tsx", "Product tile: image, name, price, short description"),
            ("frontend/src/components/ChatWidget.tsx", "Chat interface in the bottom-right corner"),
            ("frontend/src/pages/Home.tsx", "Home page (own wording, based on yalebulldogblue.com)"),
            ("frontend/src/pages/About.tsx", "About Us page (own wording, based on yalebulldogblue.com)"),
            ("frontend/src/pages/Products.tsx", "Products grid with search, category filter, sort"),
            ("frontend/src/pages/ProductPage.tsx", "Single product: large image + description, price, stock per size"),
            ("backend/main.py", "FastAPI app: products, product detail, images"),
            ("backend/requirements.txt", "Python dependencies"),
        ],
    ),
    "Problem 4 - Create account and login": (
        "Problem 4 — Create account and login",
        "problem-4--create-account-and-login",
        [
            ("backend/auth.py", "NEW: password hashing (PBKDF2), sessions, /api/auth/register, login, logout, me"),
            ("backend/main.py", "CHANGED: adds auth routes and the sessions table; images route fixed so the DB can't be downloaded"),
            ("frontend/src/auth.tsx", "NEW: AuthProvider / useAuth (who is logged in)"),
            ("frontend/src/pages/Register.tsx", "CHANGED: real Create account form (first, last, email, password, confirm)"),
            ("frontend/src/pages/Login.tsx", "CHANGED: real Log in form (email, password)"),
            ("frontend/src/components/NavBar.tsx", "CHANGED: shows 'Hi, <first name>' and Log out when logged in"),
            ("frontend/src/api.ts", "CHANGED: register, login, logout, me calls"),
            ("frontend/src/main.tsx", "CHANGED: wraps the app in AuthProvider"),
        ],
    ),
    "Problem 5 - PydanticAI agent backend": (
        "Problem 5 — PydanticAI agent backend",
        "problem-5--pydanticai-agent-backend",
        [
            ("backend/prompts/prompt.md", "NEW: system prompt (Campus Customs voice + safety rules)"),
            ("backend/agent.py", "NEW: PydanticAI agent wiring"),
            ("backend/tools.py", "NEW: tools the agent can call (search, categories; Problem 6 added the product info/stock tools)"),
            ("backend/models.py", "NEW: structured types (chat request/response, product cards, tool results)"),
            ("backend/main.py", "CHANGED: POST /api/chat and GET /api/chat/history routes"),
            ("backend/.env.example", "NEW: template for backend/.env (API key)"),
            ("backend/requirements.txt", "CHANGED: adds pydantic-ai and python-dotenv"),
            ("frontend/src/components/ChatWidget.tsx", "CHANGED: sends history, shows product cards, restores saved chat"),
            ("frontend/src/api.ts", "CHANGED: sendChat with history, getChatHistory"),
            ("frontend/src/types.ts", "CHANGED: ProductCard and ChatMessage types"),
        ],
    ),
    "Problem 6 - Tools product info and stock": (
        "Problem 6 — Tools: product info and stock",
        "problem-6--tools-product-info-and-stock",
        [
            ("backend/tools.py", "CHANGED: new get_product_description, get_product_price, get_stock tools (replace get_product_details)"),
            ("backend/models.py", "CHANGED: ProductDescription, ProductPrice, ProductStock result types (fields = catalogue columns)"),
            ("backend/prompts/prompt.md", "CHANGED: step-by-step instructions for when and how to call each tool"),
            ("backend/agent.py", "CHANGED: local_model (section 4), a rule-based PydanticAI FunctionModel the agent runs on when Claude isn't configured"),
            ("backend/main.py", "CHANGED: chat route always runs the PydanticAI agent (Claude, or local_model when Claude isn't configured)"),
        ],
    ),
    "Problem 7 - Chat search that updates the page": (
        "Problem 7 — Chat search that updates the page",
        "problem-7--chat-search-that-updates-the-page",
        [
            ("backend/models.py", "CHANGED: AgentReply.results_title; ProductCard gains description; ChatResponse.results_title"),
            ("backend/tools.py", "CHANGED: load_product_cards includes description"),
            ("backend/main.py", "CHANGED: /api/chat returns results_title with the product matches"),
            ("backend/prompts/prompt.md", "CHANGED: 'Showing products on the page' instructions"),
            ("backend/agent.py", "CHANGED: local_model handles browsing (up to 8 matches, category filter)"),
            ("frontend/src/chatResults.tsx", "NEW: shared state for the latest chat product matches"),
            ("frontend/src/components/ChatWidget.tsx", "CHANGED: pushes matches to the page and opens /products"),
            ("frontend/src/pages/Products.tsx", "CHANGED: 'From your chat' section rendered with ProductCard"),
            ("frontend/src/components/ProductCard.tsx", "CHANGED: accepts chat matches too (same card, same click-through)"),
            ("frontend/src/main.tsx", "CHANGED: wraps the app in ChatResultsProvider"),
            ("frontend/src/types.ts", "CHANGED: ProductCard.description, ChatReply.results_title"),
            ("frontend/src/index.css", "CHANGED: styles for the chat results section"),
        ],
    ),
    "Problem 8 - Customer memory": (
        "Problem 8 — Customer memory",
        "problem-8--customer-memory",
        [
            ("backend/main.py", "CHANGED: page_context_json column; history for logged-in users only; saves page context"),
            ("backend/models.py", "CHANGED: PageContext, CustomerProfile, PageInfo, ShopperContext; ChatRequest.page_context"),
            ("backend/tools.py", "CHANGED: get_shopper_context tool + build_shopper_context()"),
            ("backend/agent.py", "CHANGED: per-turn instructions with customer, page, and tools; local_model greets by name and resolves 'this' / 'the second one'"),
            ("backend/prompts/prompt.md", "CHANGED: 'Who you're talking to, and what they're looking at'"),
            ("frontend/src/api.ts", "CHANGED: sendChat sends page_context"),
            ("frontend/src/components/ChatWidget.tsx", "CHANGED: builds page context; keeps the page when answering about on-screen products"),
        ],
    ),
    "Problem 9 - Usability improvements": (
        "Problem 9 — Usability improvements",
        "problem-9--usability-improvements",
        [
            ("backend/agent.py", "CHANGED: Sonnet 5.5 by default, Opus 5.5 when a turn leans on chat history; fact_checker agent and local_fact_checker (section 3, 4)"),
            ("backend/main.py", "CHANGED: model choice, fact-check, 'Products similar' results; DELETE /api/chat/history (Start over)"),
            ("backend/tools.py", "CHANGED: find_products() + similar_products() for the 'Products similar' bubble; build_facts() for the fact-checker"),
            ("backend/models.py", "CHANGED: SimilarSearch, SimilarProducts, FactCheck; AgentReply.similar_search; ChatResponse.similar"),
            ("backend/prompts/prompt.md", "CHANGED: 'Products similar' instructions; the fact-checker's prompt at the end of the file"),
            ("backend/.env.example", "CHANGED: CC_AGENT_MODEL / CC_ESCALATION_MODEL / CC_FACTCHECK_MODEL"),
            ("frontend/src/components/ChatWidget.tsx", "CHANGED: 'Products similar' bubble and Start over button"),
            ("frontend/src/api.ts", "CHANGED: clearChatHistory()"),
            ("frontend/src/types.ts", "CHANGED: SimilarProducts; ChatReply.similar"),
            ("frontend/src/index.css", "CHANGED: bubble and Start over styles"),
        ],
    ),
    "Problem 10 - Style the website": (
        "Problem 10 — Style the website",
        "problem-10--style-the-website",
        [
            ("frontend/src/fun/points.tsx", "NEW: merch points (+10 card, +50 buy), goals (300, +100 each), rewards, activity time"),
            ("frontend/src/fun/PointsTracker.tsx", "NEW: points pill in the nav and the 'goal reached' reward toast"),
            ("frontend/src/fun/Bulldog.tsx", "NEW: Handsome Dan bulldog avatar with happy / sad / stressed moods"),
            ("frontend/src/fun/Spiders.tsx", "NEW: spiders crawling around the screen"),
            ("frontend/src/fun/Mentors.tsx", "NEW: Gon and Naruto with cycling encouraging lines per page"),
            ("frontend/src/components/ChatWidget.tsx", "CHANGED: bulldog button and header, hello animation on a new chat, mood nudge"),
            ("frontend/src/components/ProductCard.tsx", "CHANGED: +10 points and pop-out animation on click"),
            ("frontend/src/pages/ProductPage.tsx", "CHANGED: Buy button (+50 points) and confirmation"),
            ("frontend/src/components/NavBar.tsx", "CHANGED: shows the points tracker"),
            ("frontend/src/App.tsx", "CHANGED: mounts spiders, Gon and Naruto, reward toast"),
            ("frontend/src/main.tsx", "CHANGED: wraps the app in PointsProvider"),
            ("frontend/src/index.css", "CHANGED: blue/white theme, Papyrus titles, all Problem 10 animations"),
        ],
    ),
    "Problem 12 - Audit trail, safety, finish harness": (
        "Problem 12 — Audit trail, safety, finish harness",
        "problem-12--audit-trail-safety-finish-harness",
        [
            ("backend/agent.py", "CHANGED: loop limit of 5 model requests; audit trail (section 2) records each run to output/audit_trail.json"),
            ("backend/models.py", "CHANGED: cap_reply() keeps replies to one paragraph of at most 7 sentences"),
            ("backend/main.py", "CHANGED: passes the model name to run_chat and caps the fact-checked reply"),
            ("backend/prompts/prompt.md", "CHANGED: the three new safety rules, 7-sentence paragraph rule, 5-step budget"),
        ],
    ),
    "Problem 13 - Push to GitHub": (
        "Problem 13 — Push to GitHub",
        "problem-13--push-to-github",
        [
            ("backend/prompts/prompt.md", "CHANGED: now also holds the fact-checker's prompt (was prompts/factcheck.md), after a split marker"),
            ("backend/agent.py", "CHANGED: the whole agent in one file: shopping agent, audit trail, fact-checker, local models (were audit.py, factcheck.py, fallback.py)"),
            ("backend/tools.py", "CHANGED: build_facts() moved here from factcheck.py"),
            ("backend/models.py", "CHANGED (docstring only): the agent's structured types, the fourth agent file"),
            ("backend/main.py", "CHANGED: imports the agent from agent.py only"),
        ],
    ),
}

NOTE = (
    "> These are **copies** of the files this problem added or changed. The runnable app is in "
    "[`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). "
    "Files show their current version, so later problems' changes may appear too. "
    "Refresh with `python sync_problem_folders.py` from the hw 4 folder."
)


def sync_problem(folder: str, title: str, anchor: str | None, files: list[tuple[str, str]]) -> None:
    dest = ROOT / folder
    dest.mkdir(exist_ok=True)
    for sub in ("backend", "frontend"):  # only the copied trees are managed; nothing else is touched
        shutil.rmtree(dest / sub, ignore_errors=True)
    for rel, _ in files:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(APP / rel, target)

    lines = [f"# {title}", "", NOTE, ""]
    if anchor:
        lines += [f"Write-up: [output/harness.md → {title.split(' — ')[0]}]({HARNESS}#{anchor})", ""]
    lines += ["| File | What it is |", "|---|---|"]
    lines += [f"| [{rel}]({rel.replace(' ', '%20')}) | {desc} |" for rel, desc in files]
    (dest / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_problem2() -> None:
    dest = ROOT / "Problem 2 - Analyze the database"
    dest.mkdir(exist_ok=True)
    conn = sqlite3.connect(ROOT / "data" / "campus_customs.db")
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
    ).fetchall()
    counts = {name: conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0] for name, _ in rows}
    conn.close()
    schema = ["-- Schema of data/campus_customs.db (generated by sync_problem_folders.py)", ""]
    for name, sql in rows:
        schema += [f"-- {name}: {counts[name]} rows", sql.strip() + ";", ""]
    (dest / "schema.sql").write_text("\n".join(schema), encoding="utf-8")
    (dest / "README.md").write_text(
        "# Problem 2 — Analyze the database\n\n"
        f"- Write-up (every table and field, and why each matters for the website and chatbot): "
        f"[output/harness.md → Problem 2]({HARNESS}#problem-2--analyze-the-database)\n"
        "- [schema.sql](schema.sql): the database's table definitions and row counts, dumped from "
        "`data/campus_customs.db`\n",
        encoding="utf-8",
    )


def sync_problem11() -> None:
    """Problem 11 changes no app code: copy the app check page and its screenshots from output/."""
    dest = ROOT / "Problem 11 - Site testing (app check)"
    dest.mkdir(exist_ok=True)
    shutil.rmtree(dest / "app_check_images", ignore_errors=True)
    shutil.copytree(ROOT / "output" / "app_check_images", dest / "app_check_images")
    shutil.copy2(ROOT / "output" / "app_check.html", dest / "app_check.html")
    (dest / "README.md").write_text(
        "# Problem 11 — Site testing (app check)\n\n"
        "> These are **copies** of [output/app_check.html](../output/app_check.html) and its screenshots. "
        "Refresh with `python sync_problem_folders.py` from the hw 4 folder.\n\n"
        "| File | What it is |\n|---|---|\n"
        "| [app_check.html](app_check.html) | NEW: the app checks I did, one screenshot and caption per check |\n"
        "| [app_check_images/inventory.png](app_check_images/inventory.png) | NEW: the chatbot fetches stock data for Squash sweaters |\n"
        "| [app_check_images/dynamicsearchresultcards.png](app_check_images/dynamicsearchresultcards.png) "
        "| NEW: hoodie product cards the agent puts on the page |\n"
        "| [app_check_images/usabilityfeature.png](app_check_images/usabilityfeature.png) "
        "| NEW: the chatbot's Start over button |\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    sync_problem2()
    for folder, (title, anchor, files) in PROBLEMS.items():
        sync_problem(folder, title, anchor, files)
    sync_problem11()
    print("Synced:", ", ".join(["Problem 2", *[f.split(" - ")[0] for f in PROBLEMS], "Problem 11"]))
