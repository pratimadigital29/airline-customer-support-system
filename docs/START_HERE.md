# 🟢 START HERE — Simple Guide (No Video Needed)

> There is no video for this project. **Instead, the real app is running live** —
> you can click it and try it yourself. That is better than a video. 👇

## Step 1: Open the live app

The app is already running. Open the **AeroServe Demo** preview link
(it looks like `https://8000-xxxx.e2b.app`).

You will see a chat page. Click these buttons and try:

1. `✈️ Flight AI202 status` — shows flight details
2. `🎫 Booking ABC123` — shows a passenger booking
3. Type yourself: `My flight was cancelled, I need a refund urgently`
4. Type: `I want to talk to a human agent` — it creates ticket #1, #2…

👉 Then open `/docs` link (in the right side box) to see all API functions.

## Step 2: What are all these files? (Simple table)

Think of the project like a restaurant:

| Folder / File | Simple meaning |
|---|---|
| `app/static/chat.html` | 🍽️ **The dining area** — the chat page you see in browser |
| `app/routers/` | 🧾 **The waiters** — they take your request (`chat.py`, `tickets.py`, `flights.py`) |
| `app/services/` | 👨‍🍳 **The kitchen** — `triage.py` decides intent/priority, `llm.py` writes replies, `knowledge.py` finds answers |
| `app/data/` | 🗄️ **Sample data** — fake flights, bookings, FAQs (so it works with no internet/key) |
| `app/models.py` | 📝 **The notebook** — how a ticket is saved in database |
| `app/main.py` | 🚪 **The main door** — starts everything |
| `n8n/workflows/` | 🤖 **Robots** — 3 automation flows (you import these into n8n) |
| `tests/` | ✅ **Quality check** — 21 automatic tests (`pytest -q` runs them) |
| `docs/` | 📖 **Manuals** — guides like this one |
| `docker-compose.yml` | 📦 **Full pack** — runs API + database + n8n in one command |

**You only need to understand 3 files to start:**
`app/services/triage.py` (the brain) → `app/routers/chat.py` (the chat) → `app/static/chat.html` (the page).

## Step 3: What is "mock mode"?

You may have seen the words **"mock mode"**. It is simple:

- **Mock mode = FAKE mode for learning.** No API key. No money. No internet needed.
  The app uses sample answers from `app/data/` folder. Perfect for practice. ✅
- **OpenAI mode = REAL AI mode.** Needs an API key (costs money). Only for later.

👉 Stay in mock mode. It is the default. You don't need to change anything.

## Step 4: Run it on your own computer later

```bash
# 1. Download this repo from GitHub (Code → Download ZIP), open folder in terminal
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
# 2. Open http://localhost:8000 in browser — done!
```

## Step 5: What to learn first (in order)

1. Play with the chat page (10 min)
2. Read `app/services/triage.py` — see how intent/priority is decided (20 min)
3. Change one FAQ answer in `app/data/faqs.json`, restart, see your change live (10 min)
4. Run `pytest -q` — see 21 green tests (5 min)
5. Read `docs/LEARNING_PATH.md` next for the full 30-day plan

**One rule: change one small thing → run → see what happens. That is how you learn live projects.** 🚀
