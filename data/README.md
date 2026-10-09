# data/

The real data is not in the GitHub repo. `.gitignore` leaves it out. To run the app, put these files here:

| Path | What it is |
|---|---|
| `campus_customs.db` | SQLite database from the data pack: `catalogue` (102 products), `inventory`, `users`, `chat_messages`. On startup the backend adds a `sessions` table and a `page_context_json` column |
| `products/` | The 102 product photos named in `catalogue.image_file_path` (e.g. `products/<file>.jpg`) |

The backend reads this folder by default. Set `CC_DATA_DIR` to use a different one. The table definitions are in [Problem 2 - Analyze the database/schema.sql](../Problem%202%20-%20Analyze%20the%20database/schema.sql).
