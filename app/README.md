# Campus Customs app (website + API + chatbot)

The runnable app for HW 4: a React + Vite + TypeScript front end with a FastAPI backend. Problem 3 built it; Problems 4 and 5 extend it. Both parts read from the shared `data/` folder at the root of `hw 4`.

```
frontend/                React + Vite + TypeScript site
  src/components/        NavBar, ProductCard, ChatWidget (bottom-right chat)
  src/pages/             Home, Products, ProductPage, About, Login, Register
  src/fun/               Points, bulldog avatar, spiders, Gon and Naruto (Problem 10)
  vite.config.ts         Proxies /api and /images to the backend on :8000
backend/
  main.py                FastAPI app
  auth.py                Accounts, password hashing, sessions (Problem 4)
  agent.py               The agent: campus_agent, loop limit, audit trail, fact-checker, local models
  tools.py               Read-only database tools the agent can call
  models.py              Structured types for the agent, tools, and chat API
  prompts/prompt.md      Prompts: shopping assistant (voice, tools, safety rules), then the fact-checker
  .env.example           Copy to .env and add ANTHROPIC_API_KEY
  requirements.txt
```

## Run it

Use two terminals. In Git Bash or cmd, `npm` works as-is. In PowerShell, use `npm.cmd`, because the execution policy blocks `npm.ps1`.

```bash
# 1) Backend: http://localhost:8000  (API docs at /docs)
cd backend
pip install -r requirements.txt
copy .env.example .env                 # then add your ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000  # or: python -m uvicorn ... if uvicorn isn't on PATH

# 2) Frontend: http://localhost:5173
cd frontend
npm install
npm run dev
```

## Pages

| Route | Page |
|---|---|
| `/` | Home: hero, three feature blurbs (written in my own words, based on yalebulldogblue.com), and four featured products |
| `/products` | Grid of all 102 catalogue products with image, name, price, and a short description. Includes search, a category filter, and sorting |
| `/products/:id` | Single product: large image on the left; on the right, the type, name, price, description, colors, and per-size stock (in stock / only N left / out of stock) |
| `/about` | About Us (written in my own words, based on yalebulldogblue.com) |
| `/login`, `/register` | Log in and Create account, connected to the `users` table (Problem 4) |

The chat button in the bottom-right corner appears on every page.

## API (`backend/main.py`)

| Endpoint | Returns |
|---|---|
| `GET /api/health` | `{"status": "ok"}` |
| `GET /api/products` | All catalogue products, plus an `in_stock` flag |
| `GET /api/products/{product_id}` | One product, plus its `sizes` (size, quantity, in_stock), sorted XS→XXL. Returns 404 if the product doesn't exist |
| `POST /api/auth/register`, `/login`, `/logout`, `GET /api/auth/me` | Accounts and sessions. See [harness → Problem 4](../output/harness.md#problem-4--create-account-and-login) |
| `POST /api/chat` | `{"reply", "products": [ProductCard]}` from the PydanticAI agent (Problem 5) |
| `GET /api/chat/history` | A logged-in shopper's saved chat |
| `/images/products/<file>.jpg` | Product photos served from `data/products/` |

## Not done yet (left for later problems)

- "Add to cart" is a placeholder button. There is no cart or checkout.
