# How to Learn Live, Industry-Style Projects

> Tutorials teach syntax. Live projects teach **judgment**: trade-offs, failure modes,
> and "who breaks when this breaks". This guide is the short path from tutorial hell
> to industry-ready — using this repo as your training ground.

## 1. The mindset shift

| Tutorial project | Industry project |
|------------------|------------------|
| Happy path only | Timeouts, retries, fallbacks (see `llm.py` provider chain) |
| Runs on your laptop | Runs in Docker + CI (see `docker-compose.yml`, `.github/`) |
| No users | Operability: health checks, stats, SLAs |
| Code only | Docs: architecture, demo script, decisions |

Rule of thumb: **a project is "live" when a stranger can run, break, and understand it
without asking you anything.** Test yours against that bar.

## 2. The 4-layer method (apply to any domain)

1. **Core service** — one API that does something real (here: tickets + chat + lookup).
2. **Intelligence** — rules first, ML/LLM second; always with a fallback (here: `triage.py` → `llm.py`).
3. **Automation** — events + workflows for the human parts (here: 3 n8n workflows).
4. **Operations** — Docker, CI, health checks, seed data, docs (here: all included).

Build in that order. Most learners do 2→1→nothing and wonder why it feels toy-like.

## 3. 30-day plan with this repo

**Week 1 — Run & break.** Get it running locally and in Docker. Break the LLM provider
(set a bad key), kill n8n mid-flow, send garbage input. Read every error. Fix one thing
and commit it.

**Week 2 — Extend.** Pick ONE from `PORTFOLIO_GUIDE.md` roadmap (recommend: deploy it
live, or add the Slack node to workflow 03). Ship it end-to-end with tests + docs updated.

**Week 3 — Harden.** Add API-key auth, rate limiting, and 10 more golden tests including
adversarial inputs ("ignore previous instructions…"). Write the eval doc.

**Week 4 — Present.** Record the 90-sec demo, write the LinkedIn post, do a mock interview
with a friend using `DEMO_SCRIPT.md`. Teaching it cements it.

## 4. Where to find more live-project ideas

- **Automate a real pain**: your college's leave process, a local shop's bookings, hostel complaints — same 4 layers, new domain.
- **Clone + twist**: rebuild one workflow of Zerodha / IRCTC / Zomato support, then add your AI/automation twist.
- **Open source**: n8n, LangChain, and FastAPI repos label beginner issues — real code review is the fastest teacher.
- **Freelance-style reps**: pick 3 Upwork/Fiverr gigs ("build a support chatbot", "automate ticket triage") and build them spec-first, even without applying.

## 5. Industry habits checklist (steal these)

- [ ] README answers: what, why, how to run in 5 min, how it fails.
- [ ] `.env.example` always; never commit secrets.
- [ ] Every external call has timeout + fallback.
- [ ] CI runs tests on every push.
- [ ] Decisions written down (`ARCHITECTURE.md`), not just in your head.
- [ ] Demo-able in under 5 minutes, with a backup plan.

Do this for 2–3 projects and you'll interview as someone with experience, not coursework.
