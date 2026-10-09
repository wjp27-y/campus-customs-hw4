# Problem 4 — Create account and login

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 4](../output/harness.md#problem-4--create-account-and-login)

| File | What it is |
|---|---|
| [backend/auth.py](backend/auth.py) | NEW: password hashing (PBKDF2), sessions, /api/auth/register, login, logout, me |
| [backend/main.py](backend/main.py) | CHANGED: adds auth routes and the sessions table; images route fixed so the DB can't be downloaded |
| [frontend/src/auth.tsx](frontend/src/auth.tsx) | NEW: AuthProvider / useAuth (who is logged in) |
| [frontend/src/pages/Register.tsx](frontend/src/pages/Register.tsx) | CHANGED: real Create account form (first, last, email, password, confirm) |
| [frontend/src/pages/Login.tsx](frontend/src/pages/Login.tsx) | CHANGED: real Log in form (email, password) |
| [frontend/src/components/NavBar.tsx](frontend/src/components/NavBar.tsx) | CHANGED: shows 'Hi, <first name>' and Log out when logged in |
| [frontend/src/api.ts](frontend/src/api.ts) | CHANGED: register, login, logout, me calls |
| [frontend/src/main.tsx](frontend/src/main.tsx) | CHANGED: wraps the app in AuthProvider |
