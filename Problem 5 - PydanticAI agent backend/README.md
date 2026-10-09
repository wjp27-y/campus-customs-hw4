# Problem 5 — PydanticAI agent backend

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 5](../output/harness.md#problem-5--pydanticai-agent-backend)

| File | What it is |
|---|---|
| [backend/prompts/prompt.md](backend/prompts/prompt.md) | NEW: system prompt (Campus Customs voice + safety rules) |
| [backend/agent.py](backend/agent.py) | NEW: PydanticAI agent wiring |
| [backend/tools.py](backend/tools.py) | NEW: tools the agent can call (search, categories; Problem 6 added the product info/stock tools) |
| [backend/models.py](backend/models.py) | NEW: structured types (chat request/response, product cards, tool results) |
| [backend/main.py](backend/main.py) | CHANGED: POST /api/chat and GET /api/chat/history routes |
| [backend/.env.example](backend/.env.example) | NEW: template for backend/.env (API key) |
| [backend/requirements.txt](backend/requirements.txt) | CHANGED: adds pydantic-ai and python-dotenv |
| [frontend/src/components/ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) | CHANGED: sends history, shows product cards, restores saved chat |
| [frontend/src/api.ts](frontend/src/api.ts) | CHANGED: sendChat with history, getChatHistory |
| [frontend/src/types.ts](frontend/src/types.ts) | CHANGED: ProductCard and ChatMessage types |
