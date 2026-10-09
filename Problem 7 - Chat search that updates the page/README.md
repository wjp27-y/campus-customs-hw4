# Problem 7 — Chat search that updates the page

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 7](../output/harness.md#problem-7--chat-search-that-updates-the-page)

| File | What it is |
|---|---|
| [backend/models.py](backend/models.py) | CHANGED: AgentReply.results_title; ProductCard gains description; ChatResponse.results_title |
| [backend/tools.py](backend/tools.py) | CHANGED: load_product_cards includes description |
| [backend/main.py](backend/main.py) | CHANGED: /api/chat returns results_title with the product matches |
| [backend/prompts/prompt.md](backend/prompts/prompt.md) | CHANGED: 'Showing products on the page' instructions |
| [backend/agent.py](backend/agent.py) | CHANGED: local_model handles browsing (up to 8 matches, category filter) |
| [frontend/src/chatResults.tsx](frontend/src/chatResults.tsx) | NEW: shared state for the latest chat product matches |
| [frontend/src/components/ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) | CHANGED: pushes matches to the page and opens /products |
| [frontend/src/pages/Products.tsx](frontend/src/pages/Products.tsx) | CHANGED: 'From your chat' section rendered with ProductCard |
| [frontend/src/components/ProductCard.tsx](frontend/src/components/ProductCard.tsx) | CHANGED: accepts chat matches too (same card, same click-through) |
| [frontend/src/main.tsx](frontend/src/main.tsx) | CHANGED: wraps the app in ChatResultsProvider |
| [frontend/src/types.ts](frontend/src/types.ts) | CHANGED: ProductCard.description, ChatReply.results_title |
| [frontend/src/index.css](frontend/src/index.css) | CHANGED: styles for the chat results section |
