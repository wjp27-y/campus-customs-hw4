# HW 4 — Campus Customs

Campus Customs is a shopping website for Yale Bulldog Blue apparel with an AI shopping assistant. It has a React front end, a FastAPI back end, and a PydanticAI agent that answers questions about products, prices, and stock from a SQLite database.

## Layout

```
AI_prompts.md          every prompt used, by problem
requirements.txt       backend Python dependencies
.env.example           settings template: copy to .env and add your API key
.gitignore
README.md
frontend/              React + Vite + TypeScript website
backend/               FastAPI app - run with: uvicorn main:app --reload --port 8000
  main.py              web API: products, accounts and login, chat
  agent.py             the PydanticAI agents, agent loop, audit trail, fact-checker, local models
  models.py            Pydantic types for the agent, tools, and API
  tools.py             read-only database tools the agent calls
  prompts/prompt.md    the agent's prompt (and the fact-checker's, at the end)
output/
  harness.md           the harness document, one section per problem
  design.md            Problem 10 design notes
  usability.md         Problem 9 usability notes
  app_check.html       Problem 11 app check, with the screenshots in app_check_images/
  app_check_images/
  audit_trail.json     log of every agent run (Problem 12)
Problem N - …/         copies of the files each problem added or changed, plus a README
sync_problem_folders.py  refreshes the Problem folders from backend/ and frontend/

data/                  LOCAL ONLY, not in git: the data pack
  campus_customs.db
  products/
```

## How it works

```
Browser ──> React + Vite site (frontend/, :5173)
               │  /api/* and /images/* are proxied by Vite
               v
            FastAPI (backend/main.py, :8000)
               ├── products, accounts, saved chats ──> SQLite  data/campus_customs.db
               ├── product photos ──────────────────> data/products/
               └── POST /api/chat ──> PydanticAI agent (agent.py) ──> tools (tools.py) ──> SQLite
```

### Front end (`frontend/`)

React + TypeScript, built with Vite. The site only talks to the back end through `/api/...` calls in `src/api.ts`. In development, Vite forwards them to port 8000.

| Route | Page |
|---|---|
| `/` | Home: hero, three feature blurbs, and four featured products |
| `/products` | All 102 products with search, a category filter, and sorting. Products the chat finds appear here as cards |
| `/products/:id` | One product: image, type, name, price, description, colors, and stock per size |
| `/about` | About Us |
| `/login`, `/register` | Log in and Create account |

The chat widget (the bulldog in the bottom-right corner) is on every page.

### Back end (`backend/`)

| Endpoint | What it does |
|---|---|
| `GET /api/products`, `GET /api/products/{id}` | The catalogue, and one product with its stock per size |
| `POST /api/auth/register`, `/login`, `/logout`, `GET /api/auth/me` | Accounts and login sessions. Passwords are stored only as salted PBKDF2 hashes |
| `POST /api/chat` | One chat turn with the agent (below) |
| `GET /api/chat/history`, `DELETE /api/chat/history` | A logged-in shopper's saved chat, and Start over |
| `/images/products/<file>.jpg` | Product photos from `data/products/` |

For each chat message, `main.py`:

1. Loads the shopper's saved conversation (logged-in shoppers only) and what's on their page.
2. Runs the PydanticAI agent. The agent calls read-only database tools to look up products, prices, and stock, then returns a structured reply plus the product IDs to show as cards.
3. Fact-checks any price or stock claim in the reply against the database, and corrects it if it's wrong.
4. Builds the product cards straight from the database and saves the turn.

### The agent

| File | What it holds |
|---|---|
| [prompts/prompt.md](backend/prompts/prompt.md) | The shopping assistant's prompt: voice, how to use each tool, the reply format, and the safety rules. The fact-checker's prompt is at the end, after a marker line |
| [agent.py](backend/agent.py) | `campus_agent` (Claude Sonnet 5.5, escalating to Opus 5.5 for turns that lean on chat history), `run_chat` with a 5-request loop limit, the audit trail (`output/audit_trail.json`), the `fact_checker` agent, and the rule-based local models used when no API key is set |
| [tools.py](backend/tools.py) | The tools the agent can call: `search_products`, `list_categories`, `get_product_description`, `get_product_price`, `get_stock`, `get_shopper_context`. All are read-only, parameterized SQL |
| [models.py](backend/models.py) | Pydantic types for the agent's output (`AgentReply`, capped at one 7-sentence paragraph), tool results, chat requests and responses, and the fact-checker's verdict |

## Run it with the data pack

The data pack (`data(1).zip`) is local only and is never committed. It holds the SQLite database and the product photos.

**1. Add the data pack.** Unzip it into `data/` at the root of the repo:

```
data/
  campus_customs.db     catalogue, inventory, users, chat_messages
  products/             the 102 product photos (*.jpg)
```

On startup the backend adds a `sessions` table for logins and a `page_context_json` column on `chat_messages`. To keep the data somewhere else, set `CC_DATA_DIR` to that folder.

**2. Start the back end** (Python 3.11+), on http://localhost:8000:

```bash
pip install -r requirements.txt
cp .env.example .env          # Windows cmd: copy .env.example .env
# optional: put your key in .env  ->  ANTHROPIC_API_KEY=...
cd backend
uvicorn main:app --reload --port 8000
```

API docs are at http://localhost:8000/docs. With no API key the chat still works: the same PydanticAI agent runs on a built-in rule-based model instead of Claude. Add `ANTHROPIC_API_KEY` to `.env` to use Claude. `.env.example` lists the optional model and gateway settings.

**3. Start the front end** (Node 18+) in a second terminal, then open http://localhost:5173:

```bash
cd frontend
npm install
npm run dev
```

In Windows PowerShell, use `npm.cmd` if the execution policy blocks `npm`.

## Problems

| Problem | Folder | Main output |
|---|---|---|
| 1 — Vibe coder prompts | [Problem 1 - Vibe coder prompts](Problem%201%20-%20Vibe%20coder%20prompts/) | [AI_prompts.md](AI_prompts.md): every prompt, by problem |
| 2 — Analyze the database | [Problem 2 - Analyze the database](Problem%202%20-%20Analyze%20the%20database/) | [harness → Problem 2](output/harness.md#problem-2--analyze-the-database), `schema.sql` |
| 3 — Build the Campus Customs website | [Problem 3 - Build the Campus Customs website](Problem%203%20-%20Build%20the%20Campus%20Customs%20website/) | Website pages, nav bar, product grid and page, chat widget, FastAPI `backend/main.py` |
| 4 — Create account and login | [Problem 4 - Create account and login](Problem%204%20-%20Create%20account%20and%20login/) | Accounts and login in `backend/main.py`, Login/Register pages; [harness → Problem 4](output/harness.md#problem-4--create-account-and-login) |
| 5 — PydanticAI agent backend | [Problem 5 - PydanticAI agent backend](Problem%205%20-%20PydanticAI%20agent%20backend/) | `backend/agent.py`, `tools.py`, `models.py`, `prompts/prompt.md`; [harness → Problem 5](output/harness.md#problem-5--pydanticai-agent-backend) |
| 6 — Tools: product info and stock | [Problem 6 - Tools product info and stock](Problem%206%20-%20Tools%20product%20info%20and%20stock/) | `get_product_description`, `get_product_price`, `get_stock` in `backend/tools.py`; [harness → Problem 6](output/harness.md#problem-6--tools-product-info-and-stock) |
| 7 — Chat search that updates the page | [Problem 7 - Chat search that updates the page](Problem%207%20-%20Chat%20search%20that%20updates%20the%20page/) | Chat matches appear as product cards on the Products page; [harness → Problem 7](output/harness.md#problem-7--chat-search-that-updates-the-page) |
| 8 — Customer memory | [Problem 8 - Customer memory](Problem%208%20-%20Customer%20memory/) | Saved chat history for logged-in users, customer profile + page context for the agent; [harness → Problem 8](output/harness.md#problem-8--customer-memory) |
| 9 — Usability improvements | [Problem 9 - Usability improvements](Problem%209%20-%20Usability%20improvements/) | "Products similar" bubble, Start over, cheaper model, fact-checker; [usability.md](output/usability.md), [harness → Problem 9](output/harness.md#problem-9--usability-improvements) |
| 10 — Style the website | [Problem 10 - Style the website](Problem%2010%20-%20Style%20the%20website/) | Blue/white theme, Papyrus titles, bulldog chat avatar with moods, spiders, Gon and Naruto, point tracker; [design.md](output/design.md), [harness → Problem 10](output/harness.md#problem-10--style-the-website) |
| 11 — Site testing (app check) | [Problem 11 - Site testing (app check)](Problem%2011%20-%20Site%20testing%20(app%20check)/) | [app_check.html](output/app_check.html) with screenshots |
| 12 — Audit trail, safety, finish harness | [Problem 12 - Audit trail, safety, finish harness](Problem%2012%20-%20Audit%20trail,%20safety,%20finish%20harness/) | [audit_trail.json](output/audit_trail.json), safety rules, loop limit, reply cap; [harness → Problem 12](output/harness.md#problem-12--audit-trail-safety-finish-harness) |
| 13 — Push to GitHub | [Problem 13 - Push to GitHub](Problem%2013%20-%20Push%20to%20GitHub/) | This repo, its layout, and this README; [harness → Problem 13](output/harness.md#problem-13--push-to-github) |

## What's not in the repo

`.gitignore` keeps these out:

- `.env`, which holds API keys. Only `.env.example` with empty placeholders is committed.
- All of `data/`: the data pack (`campus_customs.db` and `products/`).
- `node_modules/`, `dist/`, and `__pycache__/`.

After changing code in `backend/` or `frontend/`, run `python sync_problem_folders.py` to refresh the copies in the Problem folders. It needs the data pack, because it reads the database schema for Problem 2.
