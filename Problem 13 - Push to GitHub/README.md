# Problem 13 — Push to GitHub

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 13](../output/harness.md#problem-13--push-to-github)

| File | What it is |
|---|---|
| [backend/prompts/prompt.md](backend/prompts/prompt.md) | CHANGED: now also holds the fact-checker's prompt (was prompts/factcheck.md), after a split marker |
| [backend/agent.py](backend/agent.py) | CHANGED: the whole agent in one file: shopping agent, audit trail, fact-checker, local models (were audit.py, factcheck.py, fallback.py) |
| [backend/tools.py](backend/tools.py) | CHANGED: build_facts() moved here from factcheck.py |
| [backend/models.py](backend/models.py) | CHANGED (docstring only): the agent's structured types, the fourth agent file |
| [backend/main.py](backend/main.py) | CHANGED: imports the agent from agent.py only; also loads .env from the repo root |
| [requirements.txt](requirements.txt) | MOVED: from app/backend/ to the repo root |
| [.env.example](.env.example) | MOVED: from app/backend/ to the repo root |
