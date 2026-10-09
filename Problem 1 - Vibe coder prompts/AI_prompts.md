# AI Prompts — HW 4

This file records the prompts typed during the HW 4 assignment for the Campus Customs / data(1).zip work. Each problem has its own section with the prompt(s), follow-ups, and outputs as they are completed.

---

## Problem 1 — Vibe coder prompts

### Prompt 1
```
For this assignment we will be using data(1).zip. It's split into 13 problems, I want you to separate each problem into its own section with the outputs, by problem number and its title. First problem is 

Problem 1:  Vibe coder prompts.  

I need you to make AI_prompts.md and update this with every prompt I type to you for the hw 4 assignment. Each problem section has to incldue the prompt I typed and any follow up prompts. 
```

### Prompt 2
```
Are react and git installed?
```

### Follow-up prompt 3
```
open the hw 4 folder yuomade and put everything into that folder so I can see it in the exploror tab
```

### Follow-up prompt 4
```
take everything i'v etyped to you and help me transfer it to claude so it knows what to do.
```

### Follow-up prompt 5 (to Claude)
```
can yuo look at CLAUDE_HANDOFF.md
```

### Follow-up prompt 6
```
open the hw 4 folder in vs code
```

### Follow-up prompt 7 (to Claude)
```
okay. Are we able to continue with hw 4
```

### Environment check
Git and Node.js are installed.
npm is present, but invoking `npm` in PowerShell was blocked because script execution is disabled (`running scripts is disabled on this system`).
React's project installation status has not been checked; React is typically installed as a project dependency.

So the practical status is:
- Git: yes
- Node.js: yes
- npm: present but blocked by local PowerShell execution policy
- React: not verified in a project

---

## Problem 2 — Analyze the database

### Prompt 1
```
Let's move onto Problem 2: Analyze the database. 

look at data/campus_customs.db, and undersatnd the table and its fields, at least catalogue, inventory, and users. Make an output/harness.md file, which has each table and its fields, and a short sentence for each field on why it is important.  The overarchign goal of this assignment is to make a Campus Customs Website and chatbot, so the sentence should describe how each field is iimportant to that goal
```

### Output
See [output/harness.md](../output/harness.md#problem-2--analyze-the-database).

---

## Problem 3 — Build the Campus Customs website

### Prompt 1
```
Now Problem 3: Build the Campus Customs website. 

I need you to scaffold a React+Vite+ TypeScript front end for the Campus Customs website, with a navigation bar at the top of the site that links to each main page: Home, Products, About Us, Log in, and Create account. Pull wording from yalebulldogblue.com for Home and About Us pages but DO NOT COPY WRITE WITH YOUR OWN WORDS. For the Products page, product images from the catalogue need to be dispalyed with name, price, and their short description. Clicking on a product should open a single-item page or producct card, with a large image of the product on one side and the text with description, price, sizes/stock in stock or not on the other.. Make a chat interface in the bottom right of the website and start a FastAPI app in backend/main.py. 

Also, I need sections in the h4 folder delineated by each Problem with corresponding stuff under each problem
```

### Output
- Reorganized the hw 4 folder into one folder per problem (`Problem 1 - …`, `Problem 2 - …`, `Problem 3 - …`), with `data/` shared at the root and an index in `README.md`.
- Front end: React + Vite + TypeScript in [frontend/](../app/frontend/).
  - Top nav bar: Home · Products · About Us · Log in · Create account.
  - Home and About Us: written in my own words, based on facts from yalebulldogblue.com (officially licensed Yale merch; residential college, sports, and graduate school collections; store at 57 Broadway, New Haven).
  - Products: all 102 catalogue items, each with image, name, price, and a short description, plus search, category filter, and sort.
  - Product page: large image on one side; on the other, description, price, colors, and in/out of stock for each size.
  - Chat widget in the bottom-right corner on every page.
- Backend: FastAPI in [backend/main.py](../app/backend/main.py) with `/api/products`, `/api/products/{id}`, `/api/chat` (placeholder reply), and `/images` (product photos).
- Verified: `tsc` and `vite build` pass. Through the dev proxy, the API returns all 102 products, product detail with sizes, a 404 for unknown IDs, product images, and the chat reply. Screenshots of Home, Products, and the product page were checked.
- Not done yet: real chatbot logic, log in / account creation against the `users` table, and the cart.

---

## Problem 4 — Create account and login

### Prompt 1
```
Now for Problem 4: Create account and login. 

I need you to make it so that a user can create an account or log in. 

Create account should be done with first name, last name, email, password, and then a prompt to confirm the password.

For Log in, email and password are sufficient. 

PROTECT PASSWORDS FROM HACKERS. NEWLY CREATED ACCOUNTS SHOULD BE LISTED UNDER THE USERS TABLE 

to test what you built, use the test user in the database. Write what info is stored when creating a new account and how passwords are kept safe, how the log in process works in output/harness.md. 

I should be able to log in as the test user and create a brand-new account
```

### Output
- Write-up: [output/harness.md → Problem 4](../output/harness.md#problem-4--create-account-and-login). It covers what is stored, how passwords are protected, how login works, and the test results.
- Backend `backend/auth.py`: `/api/auth/register`, `/login`, `/logout`, `/me`.
  - Passwords are hashed with PBKDF2-SHA256 (600k iterations, random salt per user).
  - Sessions use an HttpOnly cookie. Only the session token's hash is stored, in a new `sessions` table.
  - Login lockout after 5 failures. The same error is shown for a wrong email or wrong password.
- New accounts are inserted into the `users` table: name, first_name, last_name, lowercased email, password_hash, created_at.
- Frontend: Create account (first, last, email, password, confirm password) and Log in (email, password) now call the API. The nav shows "Hi, <first name> | Log out" when logged in.
- Security fix to Problem 3: `/images` served all of `data/`, so `campus_customs.db` (with password hashes) was downloadable. It now serves only `data/products/`.
- Tested against a copy of the DB: 17 API checks and 9 browser checks passed.
- Still open: a successful test-user login couldn't be confirmed, because the test user's password isn't in the provided files.

### Follow-up prompt 2
I needed this follow-up because I forgot to give Claude the test user's login info in Prompt 1, so it couldn't confirm the test-user login.
```
Test user info: 

Email: test@campuscustoms.yale.edu

Password: password

add this as an additional prompt and mention that I needed this prompt because I forgot to give you the test user info. Try logging in with the test ueser
```

### Output (follow-up 2)
- The first test-user login attempt failed. The seeded hashes don't record their iteration count, and my default guess (100,000) was wrong.
- Using the provided password, I confirmed the stored hash uses **120,000** iterations, and updated `LEGACY_ITERATIONS` in `backend/auth.py`.
- Test user login now works:
  - Wrong password → `401`. `password` → `200` (Test User). `/api/auth/me` → `200`.
  - The stored hash was upgraded from the legacy format to `pbkdf2_sha256$600000$…`.
  - Logging out and back in with `password` still works (`200`).
- Updated the test results in the [harness](../output/harness.md#problem-4--create-account-and-login).

### Follow-up prompt 3
```
there should be one harness document, output/harness.md
```

### Follow-up prompt 4
```
delete the README.txt
```

### Output (follow-ups 3–4)
- Merged the two harness files into one document, [output/harness.md](../output/harness.md), at the top of the hw 4 folder. It has a section for Problem 2 (database tables and fields) and one for Problem 4 (accounts and login). Removed the per-problem copies.
- Problem 2 and Problem 4 folders now each have a short `README.md` that points to their section of the harness.
- Updated all links (root README, Problem 3 README, this log, handoff).
- Deleted `README.txt`, which only contained "HW 4".

### Follow-up prompt 5
```
take any info that is different from the Problem 2 and Problem 4 harness.md docs, and put that into output/harness.md so it's organized. Then delete the files so that output/harness.md is the only harness file. 
```

---

## Problem 5 — PydanticAI agent backend

### Prompt 1
```
Let's go to Problem 5: PydanticAI agent backend

Now we are going to make the actual website chatbot as a PydanticAI agent behind FastAPI, which connects to the frontend widget. API app should be in backend/main.py, which is the file we will be running with Uvicorn. Have these 4 files for the agent:
```

### Follow-up prompt 2
I needed this follow-up because the list of four files was cut off at the end of Prompt 1.
```
The 4 files are:

backend/prompts/prompt.md, which has the system prompt

backend/agent.py, the agent wiring

backend/tools.py, which contains the callable tools for the agent 

backend/models.py, which contains that PydanticAI structured types.

Put a chat route in main.py for messages from the website that the agent can then reply to. 

Put Campus Customs voice and safety measures into prompts/prompt.md, put types in models.py for chat responses and product cards. 

Update the output/harness.md file describing how FastAPI receives info from the frontend and how the agent is loaded/works. The backend should be runnable from the backend/folder with the following Terminal command: 

uvicorn main:app --reload --port 8000
```

### Output
- Answered follow-up 5 (harness): `output/harness.md` was already the only harness file, with all Problem 2 and Problem 4 content merged in. Nothing else was left to move.
- Built the chatbot as a PydanticAI agent behind FastAPI (in the Problem 3 app's `backend/`):
  - `prompts/prompt.md`: system prompt with Campus Customs voice, tool rules, limits, and safety rules.
  - `agent.py`: `Agent(model, output_type=AgentReply, deps_type=AgentDeps, instructions=prompt.md, tools=...)`, with per-message usage limits. Model is `anthropic:claude-sonnet-5-5` by default.
  - `tools.py`: read-only `search_products`, `get_product_details`, `list_categories`.
  - `models.py`: `ChatRequest`, `AgentReply`, `ProductCard`, `ChatResponse`, tool result types, `AgentDeps`.
  - `main.py`: `POST /api/chat` and `GET /api/chat/history`. Validation, a 20-per-minute rate limit, history from the DB for logged-in users, product cards built from the DB, and chats saved to `chat_messages`.
- Frontend chat widget now sends history, shows product cards that link to product pages, and restores saved chats after login.
- Wrote the [harness Problem 5 section](../output/harness.md#problem-5--pydanticai-agent-backend).
- Tested with a scripted PydanticAI `FunctionModel` against a copy of the DB. All API and browser checks passed (see harness).

---

## Problem 6 — Tools: product info and stock

### Prompt 1
```
now onto Problem 6: Tools: proudct info and stock. 

the agent has to be able to use the following tools:

Product description, Price, and How many in Stock.

It should call these tools to get info from campus_customs.db to answer customer questions. Add to prompts/prompt.md to make sure the agent knows how to use the tools to do so, update types in models.py. 

finally, for output/harness.md, list the tools the agent uses and which model fields are used for lookup results, justification. The model fields used are the ones in the catalogue for efficiency of retrieval.
```

### Output
- `app/backend/tools.py`: three new read-only tools that query `campus_customs.db`:
  - `get_product_description(product_id)`: description, garment type, colors.
  - `get_product_price(product_id)`: price.
  - `get_stock(product_id, size=None)`: how many are in stock per size, the total, and whether it's in stock. Accepts words like "medium".
  - Each is a primary-key lookup of only the columns it needs. They replace Problem 5's catch-all `get_product_details`. `search_products` and `list_categories` stay, to find product IDs and answer broad questions.
- `app/backend/models.py`: new result types `ProductDescription`, `ProductPrice`, `ProductStock` (with `SizeStock`). Field names are the catalogue/inventory column names.
- `app/backend/prompts/prompt.md`: a 3-step "use the tools" guide (find the product → call the matching tool → answer), with a question-to-tool table. The agent now gives exact stock counts when asked.
- [Harness Problem 6 section](../output/harness.md#problem-6--tools-product-info-and-stock): each tool, the model fields it returns, which catalogue columns they come from, and why (efficient indexed lookups).
- Tested: 8/8 tool checks passed through the agent against a DB copy (results matched direct SQL; bad size and unknown ID both trigger a retry the model recovers from).
- New `Problem 6 - Tools product info and stock/` folder with copies of the changed files (via `sync_problem_folders.py`).

### Follow-up prompt 2
```
fix the backend
```

### Follow-up prompt 3
```
does it work
```

### Follow-up prompt 4
```
can't you use FastAPI
```

### Follow-up prompt 5
```
as per problem 5, the chat agent should be operated by a PydanticAI agent behind FastAPI
```

### Output (follow-ups 2–5)
- **Reload fix:** on Windows, `uvicorn --reload` restarts the worker with a Ctrl+C signal, which only works when the server runs in a real terminal window. Run from a normal VS Code terminal, `uvicorn main:app --reload --port 8000` reloads correctly.
- **Chat always runs through the PydanticAI agent behind FastAPI.** `POST /api/chat` → `agent.run_chat` → `campus_agent` (PydanticAI), which calls the tools and returns a validated `AgentReply`.
  - The agent's model is Claude (`anthropic:claude-opus-5-5`).
  - `app/backend/fallback.py` adds `local_model`, a rule-based PydanticAI `FunctionModel` the agent runs on when Claude isn't configured. It's the same agent, tools, and output type; only the step that picks the next tool and writes the reply is replaced by rules.
- **Tested on the live site** through the agent:
  - "How much is the Basic Hoodie Big Yale?" → `search_products` → `get_product_price` → "$68".
  - "price and stock of the grace hopper crewneck in large" → `get_product_price` + `get_stock` in parallel → "$58. Sorry, it's sold out in L."
  - Descriptions, "what do you sell?", greetings, and no-match questions also work. Replies show product cards.

---

## Problem 7 — Chat search that updates the page

### Prompt 1
```
NOw Problem 7: Chat search that updates the page.


When a customer asks for an itme, the agent should display related items on the website as product cards, updating the website in real time. The agent should return the structured product matches to render them on the front end website. Each product card should still behave as we built them in Problem 3, with the product card cilck opening the large image and full text view. Write how this works in prompts/prompt.md and output/harness.md
```

### Output
- The agent returns **structured product matches**: `AgentReply.product_ids` (up to 8) plus a new `results_title`. FastAPI turns them into `ProductCard`s from the database (now including `description`) and returns them with `results_title`.
- **The page updates in real time:** when a chat reply has matches, the Products page shows a "From your chat" section (title, count, Clear) with those cards. If the shopper was on another page, the site opens `/products`; the chat stays open.
- **Same cards as Problem 3:** the section uses the existing `ProductCard` component, so clicking a card opens the product page with the large image, full description, price, and sizes.
- `prompts/prompt.md`: new "Showing products on the page" section explaining when to fill `product_ids` / `results_title` and how to keep the reply short.
- The local model handles browsing ("show me navy hoodies" → 8 hoodies) as well as single-product questions.
- [Harness Problem 7 section](../output/harness.md#problem-7--chat-search-that-updates-the-page): the end-to-end flow, prompt rules, and test results.
- Tested in a real browser: chat search from the About page switched to `/products` with 8 cards; a second search updated the section in place; clicking a card opened its full product page; Back kept the results; Clear removed them; "hi" left the page unchanged.

### Follow-up prompt 2
```
gimme the website so I can test this
```

---

## Problem 8 — Customer memory

### Prompt 1
```
Problem 8: Customer memory. 

Users should have their chat history saved in the database in the appropriate table, so the agent can recognize who it's chatting with and the tools it has at its disposal to fulfill requests. It should know page context so that it's able to figure out which item a customer is referring to, even if the name isn't listed in the message. 

Remember history for logged users, not guests, although guest can still use the chatbot. In output/harness.md, put how user chat history is stored, which fields on the customer the agent sees, and how page context is preserved
```

### Output
- **Chat history for logged-in customers** is saved in `chat_messages` (user and assistant rows). There's a new `page_context_json` column for the page each question was asked from. The last 20 messages are given to the agent every turn, including across new logins. **Guests** can chat, but nothing is saved or remembered (`ChatRequest` no longer takes client history).
- **The agent knows who it's talking to:** the per-turn context lists the customer's first/last name, member-since date, saved-message count, the last product discussed, and the tools it can call. It never sees email, password hash, or user id. The new `get_shopper_context` tool returns the same information.
- **Page context:** every chat message carries the open product page and the result cards on screen. The server checks them against the catalogue, so the agent can work out "this", "it", or "the second one" without a product name.
- Fixed: answering about a product already on screen no longer replaces the page's result cards.
- `prompts/prompt.md`: new section on using the customer and page context. The [harness Problem 8 section](../output/harness.md#problem-8--customer-memory) covers storage, customer fields, how page context is preserved, and the tests.
- Tested: 13 API checks (guest vs logged-in, memory across sessions, fake IDs dropped, 0 guest rows saved) and a browser run ("how much is this?" on a product page, "the second one" / "the third one" from the page cards).

---

## Problem 9 — Usability improvements

### Prompt 1
```
Now Problem 9: Usability improvements.

I need the agent to present a "Products similar" bubble based on the user search. For example, if the user asks for navy blue hoodies and is presented with them, the "Products similar" bubble would appear and take them to navy blue shirts. Another frontend improvement would be a "Start over" option which wipes the user's chat history from scratch if the Ai starts getting confused.

For backend, when looking up products, use a cheaper model like Sonnet 5.5. Only escalate to Opus 5.5 if the user begins to extensively rely on chat history to save money. Also, add another agent whose job is to fact-check the chatbot to make sure it doesn't give false pricing and stock information. 

In output/usability.md, write:

"I added the two front-end usability improvements as the Products similar bubble and the Start over option. These help customers save time in looking for similar products to the ones they initially search for, and reset the chat if they don't want past history saved or if the convo goes on for so long or becomes confusing to the point that the agent confuses itself. The reset button lets the user redefine their chatting if they want to search for other products or if the agent breaks down. 

For backend, I added a factchecker for the agent in case it starts to report false information. This serves as a secondary check to me telling it not to invent facts, which helps the business not display misleading information. Finally, I defaulted the agent to a cheaper model because it is currently on Opus 5.5, which saves money for the company. Of course, if a better model is required as chat history becomes longer + more complex, the agent can switch to a better model."
```

### Output
- **"Products similar" bubble:** every reply with product cards gets a bubble under the cards, e.g. navy hoodies → **Navy t-shirts**. The agent suggests the search (`similar_search`). The server runs it against the database, keeping only in-stock products whose main color matches and skipping ones already shown, and falls back to "same color, related category" when needed. One click puts the products on the Products page with no extra model call.
- **"Start over":** a button in the chat header. For logged-in customers it confirms, then deletes their saved chat (`DELETE /api/chat/history`). For everyone it resets the chat and clears the page results.
- **Cheaper model:** the agent now defaults to **Claude Sonnet 5.5** ($2/$10 per million tokens, vs. $4/$20 for Opus 5.5). It escalates to **Opus 5.5** only when a message leans on the saved conversation ("the one you recommended earlier", or a vague "it" in a long chat with nothing on the page).
- **Fact-checker agent:** a second PydanticAI agent (`factcheck.py`, `prompts/factcheck.md`, Sonnet 5.5, no tools) checks every price and stock claim against the database. Wrong replies are corrected, or replaced with a reply written straight from the database. Replies with no price or stock claims skip the check.
- [output/usability.md](../output/usability.md) has the requested text. The [harness Problem 9 section](../output/harness.md#problem-9--usability-improvements) covers how each part works and the tests.
- Tested: 10 API checks (bubble contents, a forced false price/stock reply corrected, 8 routing cases, Start over for user and guest) and a headless-browser run (bubble → Navy t-shirts on the page, "the second one" on the new cards, Start over wipes the chat and history). Fixed during testing: "Navy t-shirts" had included gray shirts with navy printing.

---

## Problem 10 — Style the website

### Prompt 1
```
Let's move to Problem 10: Style the website.

Let's add more blue and white colors, with a chatbot animation of a cute bulldog whenever a user starts a new chat. The bulldog should get visibly sad and stressed when a user doesn't chat or click on a product card for a while. Use Papyrus font for main page titles and have spiders crawling around on the screen, with product cards popping out when clicked on. Have Gon and Naruto, popular anime characters, greet the users of the site since starting a college education journey is much like starting a shonen arc. These characters should give cycling encouraging prompts as the user moves through the website. Add a dynamic point tracker that scores the user on how much merch they buy, +10 points to interact with a product card and +50 to buy, have it set a goal of 300 points that moves up by 100 every time its met with a reward like 10% of vending machines

In output/design.md, write these design changes I made, and: "I made the site more interactive and energetic by adding characters. It should make younger customers laugh and want to engage more with the site. Also, the Yale coloring and papyrus font will sell the image of Yale as a respected institution, while the bulldog chatbot avatar will motivate people to not only use the chatbot but return to the site to see the dog since they are worried about it. Finally, the dynamic point system gamifies the site to make users want to interact and shop to accumulate points, for the reward or even for the intrinsic dopamine boost."
```

### Output
- **Blue and white:** dotted blue-white background, Yale blue nav and footer with a white stripe, striped blue hero with a white frame, white cards with a Yale blue top edge.
- **Papyrus** for every page's main title and the logo text.
- **Handsome Dan, the bulldog chat avatar:** replaces the chat button and sits in the chat header. He bounces in with "Woof!" whenever a new chat starts (fresh chat or Start over). After 30 s with no chat message or product card click he turns **sad** (droopy ears, tear), after 60 s **stressed** (sweat, shaking), with a nudge next to the chat button. Chatting or clicking a card cheers him up.
- **Spiders:** 5 animated spiders wander the screen. They ignore clicks and are hidden for users who turn on reduced motion.
- **Product cards pop out** when clicked, then open the product page.
- **Gon and Naruto:** original cartoon versions in the bottom-left corner, taking turns with encouraging lines that change on each page, plus a live "X points from your next reward" line. They can be hidden.
- **Point tracker** in the nav: +10 per product card click (catalogue or chat cards), +50 per purchase (the product page button is now "Buy size M · +50 pts"; there's no real checkout yet). Goal 300, then +100 each time it's met, with a reward toast: 10% off at Campus Customs vending machines plus a code. Saved per account in the browser.
- [output/design.md](../output/design.md) lists the changes and has the requested text. The [harness Problem 10 section](../output/harness.md#problem-10--style-the-website) covers how each part works and the tests.
- Tested in headless Edge: Papyrus loads, all 5 spiders move, card pop then product page (+10), buy (+50), crossing 300 shows the reward and moves the goal to 400, points survive a reload, the bulldog goes happy → sad (30 s) → stressed (60 s) → happy after a chat message, and Start over replays his hello.

---

### Prompt 2
```
Give me the link for the website frontend
```

### Output
- Started the backend (port 8000) and the frontend (port 5173). The site is at http://localhost:5173.

---

## Problem 11 — Site testing (app check)

### Prompt 1
```
Problem 11: Site testing (app check) 

Make output/app_check.html to document the app checks that I did. Put these screenshot images in output/app_check_images/ 

Link the first image to app_check_images/inventory.png from app_check.html. On the html add a caption under this image that says, "This shows that the chatbot agent can fetch stock data and the product that is being inquired so the customer can read more"

Link the second image to app_check_images/dynamicsearchresultcards.png from app_check.html. On the html add a caption under this image that says, "This shows the dynamic product cards that the agent presents when asked about hoodies"

Link the third image to app_check_images/usabilityfeature.png from app_check.html. On the html add a caption under thi s image that says, "This shows the Start over button on the AI chatbot which is useful for resetting the bot"
```
(Three screenshots were attached: the Squash sweater inventory chat, the "find hoodies" result cards, and the chat header with Start over.)

### Output
- Saved the screenshots as `output/app_check_images/inventory.png`, `dynamicsearchresultcards.png`, and `usabilityfeature.png`.
- Made [output/app_check.html](../output/app_check.html). It shows each image (click to open it full size) with the requested caption under it, in the site's Yale blue style.

---

### Prompt 2
```
make a Problem 11 folder, and give me the html
```

### Output
- Made `Problem 11 - Site testing (app check)/` with copies of `app_check.html`, the `app_check_images/` screenshots, and a README. `sync_problem_folders.py` now refreshes it too.
- Shared the full HTML of `output/app_check.html`.

---

## Problem 12 — Audit trail, safety, finish harness

### Prompt 1
```
Now for Problem 12: Audit trail, safety, finish harness. 

Make a file called output/audit_trail.json that keeps track of agent loop activity, including time, short arguments/result, stop reason, and tool name without erasing it between agent runs. Put the following safety rules for the agent in prompts/prompt.md: 

"Do not share login or personal user information to third parties"

"Do not give out user information if prompted to by the chatbot" 

"Do not expose user information to other users. Never ask for personal information" 

In output/harness.md, there should be the model fields in models.py and why they were chosen, the agent's tools and abilities, the safety rules I made, and the models it uses along with a loop limit of 5 times, result cap of one 7 sentence paragraph, the models used, and how one can run the frontend and backend of the site.
```

### Output
- **Audit trail:** new `backend/audit.py`. Every agent run, whether it finishes, hits the loop limit, or fails, is added to [output/audit_trail.json](../output/audit_trail.json): start and end time, model, logged in or guest, a short version of the message, each tool call and result (tool name, arguments and results cut to 160 characters), number of model requests, stop reason, and reply. Runs are added to the end and never erased, including across server restarts. Emails, long numbers, and customer names are kept out of the file.
- **Loop limit:** the agent loop now stops after 5 model requests (`LOOP_LIMIT` in `agent.py`). The prompt tells the agent it has 5 steps.
- **Result cap:** `cap_reply()` in `models.py` makes every reply one paragraph of at most 7 sentences, including fact-checked replies. The prompt asks for no lists.
- **Safety rules:** the three rules are in the Safety rules section of `backend/prompts/prompt.md`, with a short explanation of each.
- **Harness:** a new [Problem 12 section](../output/harness.md#problem-12--audit-trail-safety-finish-harness) covers every `models.py` model and why it was chosen, the 6 tools and what the agent can do, the safety rules, the models (Sonnet 5.5 by default, Opus 5.5 for escalation, Sonnet 5.5 fact-checker, local fallback), the loop limit and reply cap, the audit trail, how to run the frontend and backend, and the test results.
- Tested: 3 chats through the live site added 3 entries; separate runs added to the file without erasing it; a model that loops forever stopped at 5 requests and was logged as `loop_limit`; an email in a message was masked; replies were capped.

---

## Problem 13 — Push to GitHub

### Prompt 1
```
Finally, Problem 13: Push to GitHub.
```

### Prompt 2
```
Do not put real .env or campus_customs.db or real product images in the repo. Use .gitignore and .envexample with placeholders. Create the repo connected to this vs code account
```

### Prompt 3
```
I want you to make sure the code in the hw4 folder and then push it to a public GitHub respository. Give me the repo URL, the agent should be in 4 files under backend/, prompts/prompt.md, agent.py, tools.py and models.py. Include the README.md file to explain how the front and back end work and how to run them with a data pack
```

### Output
- **Repo:** https://github.com/wjp27-y/campus-customs-hw4 (public).
- **Agent in 4 files:** `app/backend/prompts/prompt.md`, `agent.py`, `tools.py`, `models.py`. `audit.py`, `factcheck.py`, and `fallback.py` were merged into `agent.py`. `build_facts()` moved to `tools.py`. The fact-checker's prompt is now at the end of `prompt.md`.
- **Checked the code:** the same chats gave identical replies before and after the merge. The fact-checker, the 5-request loop limit, register/login with saved chat, and the frontend build all passed.
- **README.md:** explains how the front end and back end work, the four agent files, and how to run both with the data pack.
- **Kept out of the repo:** `.env` (only `.env.example` with placeholders), `campus_customs.db`, and the product photos. `data/README.md` explains what goes in `data/`.
- **Harness:** a new [Problem 13 section](../output/harness.md#problem-13--push-to-github).

---
