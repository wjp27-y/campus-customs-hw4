# Problem 9 — Usability improvements

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 9](../output/harness.md#problem-9--usability-improvements)

| File | What it is |
|---|---|
| [backend/agent.py](backend/agent.py) | CHANGED: Sonnet 5.5 by default, Opus 5.5 when a turn leans on chat history; fact_checker agent and local_fact_checker (section 3, 4) |
| [backend/main.py](backend/main.py) | CHANGED: model choice, fact-check, 'Products similar' results; DELETE /api/chat/history (Start over) |
| [backend/tools.py](backend/tools.py) | CHANGED: find_products() + similar_products() for the 'Products similar' bubble; build_facts() for the fact-checker |
| [backend/models.py](backend/models.py) | CHANGED: SimilarSearch, SimilarProducts, FactCheck; AgentReply.similar_search; ChatResponse.similar |
| [backend/prompts/prompt.md](backend/prompts/prompt.md) | CHANGED: 'Products similar' instructions; the fact-checker's prompt at the end of the file |
| [.env.example](.env.example) | CHANGED: CC_AGENT_MODEL / CC_ESCALATION_MODEL / CC_FACTCHECK_MODEL |
| [frontend/src/components/ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) | CHANGED: 'Products similar' bubble and Start over button |
| [frontend/src/api.ts](frontend/src/api.ts) | CHANGED: clearChatHistory() |
| [frontend/src/types.ts](frontend/src/types.ts) | CHANGED: SimilarProducts; ChatReply.similar |
| [frontend/src/index.css](frontend/src/index.css) | CHANGED: bubble and Start over styles |
