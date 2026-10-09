# Problem 6 — Tools: product info and stock

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 6](../output/harness.md#problem-6--tools-product-info-and-stock)

| File | What it is |
|---|---|
| [backend/tools.py](backend/tools.py) | CHANGED: new get_product_description, get_product_price, get_stock tools (replace get_product_details) |
| [backend/models.py](backend/models.py) | CHANGED: ProductDescription, ProductPrice, ProductStock result types (fields = catalogue columns) |
| [backend/prompts/prompt.md](backend/prompts/prompt.md) | CHANGED: step-by-step instructions for when and how to call each tool |
| [backend/agent.py](backend/agent.py) | CHANGED: local_model (section 4), a rule-based PydanticAI FunctionModel the agent runs on when Claude isn't configured |
| [backend/main.py](backend/main.py) | CHANGED: chat route always runs the PydanticAI agent (Claude, or local_model when Claude isn't configured) |
