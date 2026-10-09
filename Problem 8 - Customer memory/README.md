# Problem 8 — Customer memory

> These are **copies** of the files this problem added or changed. The runnable app is in [`backend/`](../backend/) and [`frontend/`](../frontend/) (see the [README](../README.md) to run it). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 8](../output/harness.md#problem-8--customer-memory)

| File | What it is |
|---|---|
| [backend/main.py](backend/main.py) | CHANGED: page_context_json column; history for logged-in users only; saves page context |
| [backend/models.py](backend/models.py) | CHANGED: PageContext, CustomerProfile, PageInfo, ShopperContext; ChatRequest.page_context |
| [backend/tools.py](backend/tools.py) | CHANGED: get_shopper_context tool + build_shopper_context() |
| [backend/agent.py](backend/agent.py) | CHANGED: per-turn instructions with customer, page, and tools; local_model greets by name and resolves 'this' / 'the second one' |
| [backend/prompts/prompt.md](backend/prompts/prompt.md) | CHANGED: 'Who you're talking to, and what they're looking at' |
| [frontend/src/api.ts](frontend/src/api.ts) | CHANGED: sendChat sends page_context |
| [frontend/src/components/ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) | CHANGED: builds page context; keeps the page when answering about on-screen products |
