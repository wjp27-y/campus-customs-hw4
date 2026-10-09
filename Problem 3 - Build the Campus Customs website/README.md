# Problem 3 — Build the Campus Customs website

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

| File | What it is |
|---|---|
| [frontend/package.json](frontend/package.json) | React + Vite + TypeScript project and dependencies |
| [frontend/index.html](frontend/index.html) | HTML entry point |
| [frontend/vite.config.ts](frontend/vite.config.ts) | Dev server; proxies /api and /images to FastAPI |
| [frontend/tsconfig.json](frontend/tsconfig.json) | TypeScript settings |
| [frontend/src/main.tsx](frontend/src/main.tsx) | React entry point and router |
| [frontend/src/App.tsx](frontend/src/App.tsx) | Routes for every page, plus footer and chat widget |
| [frontend/src/index.css](frontend/src/index.css) | Site styles (Yale blue theme) |
| [frontend/src/api.ts](frontend/src/api.ts) | Calls to the backend API |
| [frontend/src/types.ts](frontend/src/types.ts) | TypeScript types for products |
| [frontend/src/components/NavBar.tsx](frontend/src/components/NavBar.tsx) | Top navigation bar: Home, Products, About Us, Log in, Create account |
| [frontend/src/components/ProductCard.tsx](frontend/src/components/ProductCard.tsx) | Product tile: image, name, price, short description |
| [frontend/src/components/ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) | Chat interface in the bottom-right corner |
| [frontend/src/pages/Home.tsx](frontend/src/pages/Home.tsx) | Home page (own wording, based on yalebulldogblue.com) |
| [frontend/src/pages/About.tsx](frontend/src/pages/About.tsx) | About Us page (own wording, based on yalebulldogblue.com) |
| [frontend/src/pages/Products.tsx](frontend/src/pages/Products.tsx) | Products grid with search, category filter, sort |
| [frontend/src/pages/ProductPage.tsx](frontend/src/pages/ProductPage.tsx) | Single product: large image + description, price, stock per size |
| [backend/main.py](backend/main.py) | FastAPI app: products, product detail, images |
| [requirements.txt](requirements.txt) | Python dependencies (at the repo root) |
