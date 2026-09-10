# 📘 Step-by-Step: Docker, n8n, PostgreSQL, SQLite
### For non-developers (marketing people welcome 🙂)

> You do **NOT** need to become a coder. You only need to **understand + click + copy-paste**.
> Your AeroServe project is your playground — everything below uses it.

## 🗺️ The big picture (read this first — 2 min)

Your project uses 4 tools. Here is what each one is, in simple words:

| Tool | One-line meaning | Marketing analogy |
|---|---|---|
| **SQLite** | A database in **one small file** | 📓 A personal diary — only you write in it |
| **PostgreSQL** | A database for **teams & big apps** | 🏢 Office CRM — whole team uses it together |
| **Docker** | A **lunchbox** that packs an app + everything it needs | 🍱 Tiffin box — same food, works anywhere |
| **n8n** | **"If this happens, do that"** robot, drag-and-drop, no code | 🤖 Like Zapier, but free |

How they connect in YOUR project:

```
Customer types message → App saves ticket in SQLite/PostgreSQL
                       → Docker runs the whole app in a box
                       → n8n robot sees new ticket → alerts the team
```

**Learning order (2 weeks, 30 min/day):**

| Week | Topic | Why in this order |
|---|---|---|
| Days 1–3 | SQLite | Easiest. It's just a file. Quick win. |
| Days 4–7 | PostgreSQL | Same idea as SQLite, but for teams. |
| Days 8–11 | Docker | Now you pack everything in a box. |
| Days 12–14 | n8n | Most fun. Visual robots, zero code. 🎉 |

---

## Part 1: SQLite — Days 1–3 📓

### What is it?
SQLite is a **database inside one file**. In your project that file is called **`support.db`**.
All 3 sample tickets I created for you are saved inside that one file. Nothing else needed.

Think: **SQLite = Excel file. One file, open it, see tables.**

### Step 1 — See your data (no install, 2 min)
1. Open your live app preview link (AeroServe Demo).
2. Add this at the end of the address: `/api/v1/tickets`
   Example: `https://8000-xxxx.e2b.app/api/v1/tickets`
3. You see your 3 tickets. 👏 **That data came from SQLite.**

### Step 2 — Install DB Browser (free tool, 5 min)
This tool lets you **open the database file and see tables**, like Excel.
1. Go to **https://sqlitebrowser.org** → Download → Install (Windows/Mac both OK).
2. On your computer, open the project folder → find **`support.db`**.
   (Run the app once first — the file is created automatically.)
3. In DB Browser: **Open Database → select `support.db` → Browse Data → table `tickets`**.
4. 🎉 You see rows = tickets, columns = subject, priority, intent…

### Step 3 — Try 3 copy-paste queries (10 min)
In DB Browser, click **Execute SQL** tab. Copy-paste one by one, press ▶ Run:

```sql
-- 1. Show all tickets (SELECT = "show me")
SELECT id, subject, priority, intent FROM tickets;

-- 2. Show only urgent/high priority (WHERE = "filter")
SELECT id, subject, priority FROM tickets WHERE priority IN ('urgent', 'high');

-- 3. Count tickets by priority (like a pivot table!)
SELECT priority, COUNT(*) FROM tickets GROUP BY priority;
```

✅ **You learned:** database = file, table = sheet, row = one ticket, SQL = asking questions.

---

## Part 2: PostgreSQL — Days 4–7 🏢

### What is it?
PostgreSQL ("Postgres") is **SQLite's big brother for companies**:
- SQLite = one file, one user → good for learning & small apps.
- Postgres = a **server** (always running program), many users at once → good for real business.

Think: **SQLite = personal diary 📓 → Postgres = company CRM 🏢.**
Good news: **90% of what you learned in SQLite works exactly the same.**

| | SQLite | PostgreSQL |
|---|---|---|
| What | One file (`support.db`) | A running server |
| Users | 1 at a time | 1000s at same time |
| Setup | Zero | Install once |
| Used when | Learning, small apps, mobile | Real websites, companies |

### Step 1 — Install (pick ONE, 10 min)
- **Easiest (Windows/Mac):** install **Docker Desktop** (we need it later anyway),
  then run Postgres with ONE command (see Part 3, Step 2).
- **OR without Docker:** download from **https://www.postgresql.org/download** → install → remember the password you set.

### Step 2 — Run Postgres with one command (2 min)
Open terminal / PowerShell, paste:

```bash
docker run --name my-postgres -e POSTGRES_PASSWORD=learn123 -p 5432:5432 -d postgres:16
```

In simple words: *"Docker, please start a Postgres box for me with password learn123."*

### Step 3 — See tables visually with pgAdmin (10 min)
1. Download **pgAdmin** (free, like DB Browser but for Postgres): **https://www.pgadmin.org**
2. Add server: Host = `localhost`, Password = `learn123` → Connect.
3. Browse databases → tables. Run the **same 3 queries from Part 1** — they work here too!

✅ **You learned:** Postgres = shared database server; same SQL; tools show tables visually.

---

## Part 3: Docker — Days 8–11 🍱

### What is it?
Problem Docker solves: *"It works on my laptop but not on yours!"*
Docker packs the app + settings + everything into a **box (container)**. The box runs **exactly the same** on any computer.

Think: **Docker = tiffin/lunchbox.** 🍱
- **Image** = the recipe + packed food (stored, not running). Example: `postgres:16`.
- **Container** = the lunchbox you are **eating from right now** (running).

Your project has a file `docker-compose.yml` = **"lunch order for 3 boxes"**: API box + Postgres box + n8n box, all starting together.

### Step 1 — Install Docker Desktop (15 min)
1. Go to **https://www.docker.com/products/docker-desktop** → Download (Windows/Mac) → Install → Start it.
2. Open terminal / PowerShell, paste to check:
```bash
docker --version
```
If you see a version number → installed! 🎉

### Step 2 — Run YOUR project with one command (5 min)
1. Open terminal **inside your project folder** (where `docker-compose.yml` is).
2. Paste:
```bash
docker compose up -d
```
3. Wait 1–2 min. Then open:
   - App: **http://localhost:8000** (your chat page!)
   - n8n: **http://localhost:5678** (robots page!)
4. 🎉 Your full project is running in boxes.

### Step 3 — Learn 4 commands (copy-paste, 10 min)
```bash
docker ps              # show running boxes (like Task Manager)
docker logs <name>     # see what a box is saying (replace <name>)
docker compose down    # stop all boxes
docker compose up -d   # start all boxes again
```

✅ **You learned:** image = packed box, container = running box, compose = start many boxes together.

---

## Part 4: n8n — Days 12–14 🤖 (most fun!)

### What is it?
n8n is a **visual robot builder**. You drag boxes, connect them with lines, no coding.
Example: *"When a new ticket comes → send message to team."*

Think: **n8n = Zapier, but free and you own it.**
(If you ever used Zapier, Make, or even Gmail filters — same idea.)

### Step 1 — Open n8n (2 min)
1. Make sure Docker boxes are running (Part 3, Step 2).
2. Open **http://localhost:5678** → create account (any email, stored locally).
3. You see a blank canvas. This is where robots are built. 🤖

### Step 2 — Import workflow 01 from YOUR project (5 min)
1. In n8n: click **⋯ menu → Import from File**.
2. Pick file: `n8n/workflows/01-ticket-triage.json` from this project.
3. You now see boxes connected: **Webhook → Evaluate → Human? → Escalate/Assign**.
4. Click **Inactive → Active** (top right). Your robot is ON. 🟢

### Step 3 — Watch the robot work LIVE (10 min)
1. In your app (localhost:8000), create an urgent ticket via chat:
   type `Stranded at airport, flight cancelled, need help urgently!`
2. Go back to n8n → click **Executions** (left menu).
3. 🎉 You SEE the robot run: green lines show the path it took!
4. Click each box to see what data went in and out. **This is how you learn automation.**

### Step 4 — Build your FIRST own robot (20 min, no code!)
Build: *"Every morning 9 AM → get ticket stats → send to team."*
1. New workflow → add **Schedule Trigger** (set 9:00 AM).
2. Add **HTTP Request**: GET `http://api:8000/api/v1/tickets/stats/summary`.
3. Add **Gmail / Slack / Telegram** node → connect your account → send the stats.
4. Activate. Done. You built office automation. 🚀

✅ **You learned:** trigger → action → action; webhooks = doorbells; executions = CCTV replay.

---

## 💼 Why should a MARKETING person learn these?

| Skill | Your marketing superpower |
|---|---|
| n8n | Auto-send leads from form → CRM → WhatsApp follow-up. Daily reports to Sheets. No developer needed. |
| SQLite/Postgres | Understand where customer data lives. Ask analysts the right questions. Read simple reports yourself. |
| Docker | Run any demo/tool yourself. Say "I tested it locally" in meetings. Developers will respect you. 😄 |
| APIs (bonus, you already have `/docs`) | Connect tools together. Marketing automation = APIs + n8n. |

## 📖 Mini dictionary (only 10 words!)

| Word | Simple meaning |
|---|---|
| **Database** | Smart Excel that apps use |
| **Table** | One sheet (e.g. `tickets`) |
| **Row** | One line = one ticket/order/user |
| **SQL / Query** | Asking the database a question |
| **API** | A counter where apps order data (your `/docs` page lists all dishes) |
| **JSON** | Data written as `{ "name": "Priya" }` — apps pass notes in this format |
| **Image** | Packed lunchbox (not running) |
| **Container** | Lunchbox being eaten (running) |
| **Webhook** | A doorbell — "hey! something happened!" |
| **Workflow** | Robot's to-do list in n8n |

## ✅ Your 2-week checklist

- [ ] Days 1–3: Opened `/api/v1/tickets`, installed DB Browser, ran 3 queries
- [ ] Days 4–7: Started Postgres, opened pgAdmin, ran same queries
- [ ] Days 8–11: Installed Docker Desktop, ran `docker compose up -d`, opened app + n8n
- [ ] Days 12–14: Imported workflow 01, watched an Execution, built my own robot
- [ ] Bonus: connected n8n to my Gmail/Sheets/Slack

**Golden rule: 30 minutes a day, always click + try, never just read.** 🚀
