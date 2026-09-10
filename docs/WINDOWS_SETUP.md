# 🪟 Windows Setup — Exact Clicks (Windows 10 / 11)

> Follow in order. **Do only Steps 1–4 today.** Rest can wait for tomorrow.
> Time needed: ~30 minutes.

## Before you start
- You need: Windows 10 or 11, 64-bit. (Check: Settings → System → About.)
- You will use **PowerShell** = the black/blue command window in Windows.
  Open it: press `Windows key` → type `PowerShell` → Enter.

---

## Step 1: Install Python (10 min) 🐍

1. Go to **https://www.python.org/downloads** → big yellow **Download Python** button → run the file.
2. ⚠️ **VERY IMPORTANT:** on the first screen, TICK the box **`Add python.exe to PATH`** (bottom). Then click **Install Now**.
   - If you forget this box, nothing will work. Uninstall and do again.
3. When finished, open PowerShell and paste:
   ```powershell
   python --version
   ```
   If you see `Python 3.11` or `3.12` → success! 🎉

## Step 2: Download this project (3 min) 📥

No coding tools needed — just download:

1. Open the GitHub repo page in browser.
2. Click green **`<> Code`** button → **Download ZIP**.
3. Go to Downloads folder → Right-click ZIP → **Extract All** → extract to `Documents`.
4. You now have a folder like `Documents\airline-customer-support-system-...`. Open it.
   (That long name is OK. Keep it.)

## Step 3: Open PowerShell INSIDE the project folder (1 min) 📂

1. Open the extracted project folder in File Explorer.
2. Click the **address bar** at top (shows the folder path) → type `powershell` → press Enter.
3. A PowerShell window opens, already inside your project. 👍
   - Check: paste `dir` → you should see `docker-compose.yml`, `app`, `docs`...

## Step 4: Run YOUR app (10 min) 🚀

Paste these **one by one** in that PowerShell window (wait for each to finish):

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\activate
```
> ⚠️ If you see a red error about "execution policy", paste this ONCE, then try activate again:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

```powershell
pip install -e ".[dev]"
```
(This downloads everything. Takes 2–3 minutes. ☕)

```powershell
uvicorn app.main:app --reload
```

Now open in browser: **http://localhost:8000** 🎉
You see YOUR chat app running on YOUR computer!

- To stop: click the PowerShell window → press `Ctrl + C`.
- To start again later: open PowerShell in folder (Step 3) → `.venv\Scripts\activate` → `uvicorn app.main:app --reload`.

## Step 5: See the database file (5 min) 📓

1. Install **DB Browser for SQLite**: **https://sqlitebrowser.org/dl** → download Windows version → Next-Next-Finish.
2. In DB Browser: **Open Database** → go to your project folder → select **`support.db`** → Open.
3. Click **Browse Data** tab → table `tickets` → you see all tickets! Each row = one ticket.
4. Click **Execute SQL** tab → paste → press ▶:
   ```sql
   SELECT id, subject, priority, intent FROM tickets;
   ```

## Step 6: Install Docker Desktop (15 min + restart) 🐳

1. Go to **https://www.docker.com/products/docker-desktop** → **Download for Windows** → run installer → OK/Next → **Close and restart** computer.
2. After restart, open **Docker Desktop** from Start menu. Wait 2–3 min until the bottom-left corner turns **green** ("Engine running"). 🟢
3. Open PowerShell, paste:
   ```powershell
   docker --version
   ```
   Version number = success! 🎉

> ⚠️ If Docker shows a **WSL2 error**: open PowerShell **as Administrator**
> (right-click PowerShell → Run as administrator) → paste `wsl --install` → restart PC → open Docker again.
>
> ⚠️ If Docker says **"Virtualization not enabled"**: restart PC → keep pressing `F2` or `Del` during startup to enter BIOS → find **Virtualization Technology** → **Enable** → Save & Exit. (Ask a techy friend if this step scares you — it takes them 2 minutes.)

## Step 7: Run EVERYTHING with one command (5 min) 🤖

1. Open PowerShell in project folder (Step 3).
2. Make sure Docker Desktop is open and green. 🟢
3. Paste:
   ```powershell
   docker compose up -d
   ```
4. Wait 1–2 min. Open:
   - App: **http://localhost:8000**
   - n8n robots: **http://localhost:5678** (create account with any email)
5. To stop everything: `docker compose down`.

**Now continue with Part 4 (n8n) in `LEARN_STEP_BY_STEP.md`** — import workflow 01 and watch your first robot run! 🎉

---

## 🆘 Common problems (Windows)

| Problem | Fix (copy-paste) |
|---|---|
| `python` is not recognized | Python installed WITHOUT PATH box → reinstall, tick `Add python.exe to PATH` |
| Red "execution policy" error | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` then retry |
| `pip install` brackets error | Use quotes exactly: `pip install -e ".[dev]"` |
| Port 8000 already in use | Another app is running → stop old PowerShell window (`Ctrl+C`) |
| `docker` is not recognized | Docker Desktop not open → open it, wait for green, retry |
| Docker WSL2 error | Admin PowerShell → `wsl --install` → restart PC |
| n8n page won't open | Wait 1 min more, then `docker compose up -d` again |

**Still stuck? Copy the FULL red error message and send it to me. I will fix it with you.** 🙂
