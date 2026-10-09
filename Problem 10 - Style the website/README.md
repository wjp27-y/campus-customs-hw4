# Problem 10 — Style the website

> These are **copies** of the files this problem added or changed. The runnable app is in [`app/`](../app/) (run it from there; see [app/README.md](../app/README.md)). Files show their current version, so later problems' changes may appear too. Refresh with `python sync_problem_folders.py` from the hw 4 folder.

Write-up: [output/harness.md → Problem 10](../output/harness.md#problem-10--style-the-website)

| File | What it is |
|---|---|
| [frontend/src/fun/points.tsx](frontend/src/fun/points.tsx) | NEW: merch points (+10 card, +50 buy), goals (300, +100 each), rewards, activity time |
| [frontend/src/fun/PointsTracker.tsx](frontend/src/fun/PointsTracker.tsx) | NEW: points pill in the nav and the 'goal reached' reward toast |
| [frontend/src/fun/Bulldog.tsx](frontend/src/fun/Bulldog.tsx) | NEW: Handsome Dan bulldog avatar with happy / sad / stressed moods |
| [frontend/src/fun/Spiders.tsx](frontend/src/fun/Spiders.tsx) | NEW: spiders crawling around the screen |
| [frontend/src/fun/Mentors.tsx](frontend/src/fun/Mentors.tsx) | NEW: Gon and Naruto with cycling encouraging lines per page |
| [frontend/src/components/ChatWidget.tsx](frontend/src/components/ChatWidget.tsx) | CHANGED: bulldog button and header, hello animation on a new chat, mood nudge |
| [frontend/src/components/ProductCard.tsx](frontend/src/components/ProductCard.tsx) | CHANGED: +10 points and pop-out animation on click |
| [frontend/src/pages/ProductPage.tsx](frontend/src/pages/ProductPage.tsx) | CHANGED: Buy button (+50 points) and confirmation |
| [frontend/src/components/NavBar.tsx](frontend/src/components/NavBar.tsx) | CHANGED: shows the points tracker |
| [frontend/src/App.tsx](frontend/src/App.tsx) | CHANGED: mounts spiders, Gon and Naruto, reward toast |
| [frontend/src/main.tsx](frontend/src/main.tsx) | CHANGED: wraps the app in PointsProvider |
| [frontend/src/index.css](frontend/src/index.css) | CHANGED: blue/white theme, Papyrus titles, all Problem 10 animations |
