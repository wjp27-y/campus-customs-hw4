# Problem 12 — Audit trail, safety, finish harness

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 12](../output/harness.md#problem-12--audit-trail-safety-finish-harness)

| File | What it is |
|---|---|
| [backend/agent.py](backend/agent.py) | CHANGED: loop limit of 5 model requests; audit trail (section 2) records each run to output/audit_trail.json |
| [backend/models.py](backend/models.py) | CHANGED: cap_reply() keeps replies to one paragraph of at most 7 sentences |
| [backend/main.py](backend/main.py) | CHANGED: passes the model name to run_chat and caps the fact-checked reply |
| [backend/prompts/prompt.md](backend/prompts/prompt.md) | CHANGED: the three new safety rules, 7-sentence paragraph rule, 5-step budget |
