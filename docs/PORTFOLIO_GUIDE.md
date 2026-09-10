# Portfolio Guide — turning this repo into job offers

## What recruiters scan for (and where this repo answers it)

| Recruiter question | Your evidence |
|--------------------|---------------|
| Can they ship end-to-end? | Chat UI → API → DB → n8n, `docker compose up` runs it all |
| Do they understand AI beyond prompts? | Grounded generation, provider fallback, deterministic routing |
| Do they test? | 21 tests + CI badge in README |
| Can they operate it? | `/health`, `/ready`, compose healthchecks, SLA watchdog |
| Can they communicate? | README, architecture doc, demo script, this guide |

## Resume bullets (copy-paste, then make them yours)

- Built **AeroServe**, an AI airline support system (FastAPI, SQLAlchemy, n8n) that triages tickets by intent/sentiment/priority and drafts grounded replies — runs offline in mock mode or with OpenAI/Ollama.
- Designed an **event-driven automation loop**: API webhooks → 3 n8n workflows (triage routing, 15-min SLA watchdog, feedback sentiment) → callback API; urgent issues auto-escalate to a duty manager.
- Shipped **production practices**: Docker Compose (API + Postgres + n8n), GitHub Actions CI, health/readiness probes, 21 pytest tests, live dashboard UI.

## LinkedIn / GitHub polish checklist

- [ ] Pin this repo on your GitHub profile.
- [ ] Add an `About` line: "AI airline support: FastAPI + LLM triage + n8n automation — docker compose up to run".
- [ ] Record a 90-second demo (use `docs/DEMO_SCRIPT.md`, OBS or Loom) and link it in the README.
- [ ] Post: problem → what you built → one screenshot → repo link → "happy to walk through the architecture".
- [ ] Add topics: `fastapi` `llm` `n8n` `python` `automation` `customer-support`.

## Extension roadmap (each = one strong commit + one interview story)

1. **Real RAG** — pgvector + embeddings over a policy PDF; show before/after answer quality.
2. **Evals in CI** — 50-message golden set, fail CI if intent accuracy drops below threshold.
3. **Auth + rate limits** — API keys, per-IP throttling on `/chat`.
4. **WhatsApp adapter** — n8n WhatsApp trigger → `/chat` → reply; screenshot the phone convo.
5. **Deploy it** — Render/Fly.io for API + Postgres; post the live URL in the README.
   A live link multiplies recruiter attention more than any other single step.

## Interview Q&A prep

- *"Why not pure LLM for everything?"* → Cost, latency, determinism. Routing must be testable; generation can be fuzzy.
- *"How do you prevent hallucination?"* → Grounding block from verified sources, short max-tokens, templates as floor.
- *"How would you scale this?"* → See `ARCHITECTURE.md` scaling notes — read them aloud once before the call.
