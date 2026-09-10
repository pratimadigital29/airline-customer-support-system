# ✈️ AeroServe — Airline Customer Support System

AI-triaged support tickets + live flight & booking lookup + n8n automation.
**Python · FastAPI · LLM (OpenAI/Ollama/mock) · n8n · Postgres · Docker**

A customer types *"My PNR is RTY321, my flight got cancelled"* → the system classifies
intent, detects sentiment, assigns priority, grounds an answer in real booking/flight
data, and escalates to humans via n8n when needed. Runs **fully offline** in mock mode —
no API keys required.

## ✨ Features

| Area | What it does |
|------|--------------|
| 💬 **AI chat** (`/`) | Flight status, PNR booking lookup, refund/baggage policies, human handoff with auto-ticketing |
| 🎟️ **Smart tickets** | Every ticket gets intent + confidence + sentiment + priority + SLA + drafted reply |
| 🧠 **LLM with fallback** | OpenAI → Ollama → grounded templates. Routing stays deterministic & unit-tested |
| 🔁 **n8n automation** | 3 import-ready workflows: triage routing, 15-min SLA watchdog, feedback sentiment loop |
| 📊 **Ops dashboard** | Live stats (`/api/v1/tickets/stats/summary`) + health/readiness probes |
| 🐳 **One-command run** | `docker compose up` → API + Postgres + n8n |

## 🚀 Quickstart

**Option A — local (fastest, no Docker):**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open **http://localhost:8000** → chat UI · **/docs** → interactive API docs.

**Option B — full stack with n8n:**

```bash
docker compose up -d
# API → http://localhost:8000 · n8n → http://localhost:5678
```

Then import workflows from `n8n/workflows/` (see [`n8n/README.md`](n8n/README.md)) and activate them.

**Option C — real LLM (optional):**

```bash
cp .env.example .env
# set LLM_PROVIDER=openai + OPENAI_API_KEY, or LLM_PROVIDER=ollama
```

## 🔌 API examples

```bash
# Chat with booking + flight grounding
curl -X POST localhost:8000/api/v1/chat -H 'Content-Type: application/json' \
  -d '{"message":"My PNR is ABC123, is my flight on time?"}'

# Create an auto-triaged ticket
curl -X POST localhost:8000/api/v1/tickets -H 'Content-Type: application/json' \
  -d '{"subject":"Stranded!","message":"Flight AI860 cancelled, stranded at airport with medical issue","customer_name":"Priya"}'

# Ops stats, flight status, booking lookup
curl localhost:8000/api/v1/tickets/stats/summary
curl localhost:8000/api/v1/flights/6E234
curl localhost:8000/api/v1/bookings/ABC123

# n8n callback: escalate a ticket
curl -X POST localhost:8000/api/v1/webhooks/n8n/ticket-event -H 'Content-Type: application/json' \
  -d '{"ticket_id":1,"action":"escalate"}'
```

Try these PNRs: `ABC123` · `XYZ789` · `RTY321` (cancelled flight) · `MNB654`
Try these flights: `AI202` · `6E234` (delayed) · `AI860` (cancelled)

## 🏗️ Project structure

```
app/
├── main.py            # FastAPI factory, versioned routers, static UI
├── config.py          # 12-factor settings (env-driven)
├── models.py / schemas.py / database.py
├── routers/           # health · tickets · chat · flights · webhooks
├── services/
│   ├── triage.py      # deterministic intent/sentiment/priority + SLA
│   ├── llm.py         # OpenAI/Ollama/mock provider chain
│   └── knowledge.py   # FAQs, flights, bookings (PSS/GDS seam)
├── data/              # seed FAQs, flights, bookings
└── static/chat.html   # demo chat UI + dashboard
n8n/workflows/         # 01-triage · 02-SLA watchdog · 03-feedback loop
tests/                 # 21 pytest tests (unit + API integration)
docs/                  # architecture · demo script · portfolio guide · learning path
```

## 🧪 Tests & CI

```bash
pytest -q            # 21 tests, isolated test DB
```

GitHub Actions runs the suite on every push (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## 📚 Docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system diagram, design decisions, scaling notes
- [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — 5-minute interview demo, minute by minute
- [`docs/PORTFOLIO_GUIDE.md`](docs/PORTFOLIO_GUIDE.md) — resume bullets, LinkedIn checklist, extension roadmap
- [`docs/LEARNING_PATH.md`](docs/LEARNING_PATH.md) — how to learn live industry projects (the method behind this repo)
- [`n8n/README.md`](n8n/README.md) — workflow setup + end-to-end test

## 🗺️ Roadmap

- [ ] pgvector RAG over full policy manual
- [ ] Golden-set intent evals in CI
- [ ] API-key auth + rate limiting
- [ ] WhatsApp adapter via n8n
- [ ] Live deployment (Render/Fly.io) + demo video

## 📄 License

MIT — see [LICENSE](LICENSE).
