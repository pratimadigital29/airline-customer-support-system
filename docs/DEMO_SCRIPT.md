# 5-Minute Demo Script (for interviews & recordings)

> Goal: prove you can **design, build, automate, and operate** a system — not just code.

## 0:00 — The hook (30 sec)

"Airlines drown in support tickets — delays, cancellations, lost bags. I built
AeroServe: a customer types a message, the system classifies intent, detects
sentiment, assigns priority, grounds an answer in real booking and flight data,
and escalates to humans via n8n when needed. It runs fully offline in mock mode,
or with OpenAI/Ollama via one env var."

## 0:30 — Live chat (90 sec)

Open `/` and run these in order:

1. `What is the status of flight AI202?` → live flight card in the reply.
2. `My PNR is RTY321, my flight got cancelled` → booking + **Cancelled** status
   + rebooking policy. Point at the `intent / confidence / sentiment` meta line.
3. `I want to talk to a human agent` → priority ticket `#N` created. Open
   `/api/v1/tickets/N` to show the persisted triage + suggested reply.

Say: *"Every reply carries its sources — grounding first, generation second."*

## 2:00 — Automation (90 sec)

1. Show `GET /api/v1/tickets/stats/summary` — the ops dashboard feed.
2. Open n8n workflow **01**: "API fires a webhook on every ticket; urgent ones
   auto-escalate to the duty manager." Show the Executions tab if live.
3. Mention workflow **02** (SLA watchdog every 15 min) and **03** (feedback loop).

Say: *"Business rules live in tested code; human orchestration lives in
workflows — each changes at its own pace."*

## 3:30 — Code walkthrough (60 sec)

Show three files, 20 seconds each:

- `app/services/triage.py` — "deterministic, unit-tested routing contract"
- `app/services/llm.py` — "provider chain with graceful degradation"
- `tests/` + `pytest -q` — "21 tests, green, running in GitHub Actions"

## 4:30 — Close (30 sec)

"If I had one more sprint: pgvector RAG over the full policy manual, WhatsApp
adapter in n8n, and a golden-set eval in CI. The seams are already there —
`knowledge.search_faqs` and the webhook contracts."

## Backup (if demo gods fail)

- `curl` examples in the README work even if the UI doesn't.
- Screenshots: take 2 (chat UI + n8n execution) and keep them in `docs/` before any interview.
