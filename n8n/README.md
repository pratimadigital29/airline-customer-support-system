# n8n Automation Workflows

Three import-ready workflows that turn the API into an **event-driven support operation**.
They run against the compose stack (`API_BASE_URL=http://api:8000/api/v1` is pre-set in `docker-compose.yml`).

| # | Workflow | Trigger | What it does |
|---|----------|---------|--------------|
| 01 | Ticket Triage | Webhook `new-ticket` | Scores every new ticket; urgent → escalate to duty-manager, else auto-assign |
| 02 | SLA Breach Escalation | Every 15 min | Polls open tickets, escalates any past its SLA window |
| 03 | Feedback Sentiment Loop | Webhook `feedback` | Scores feedback via the API; negative ratings escalate + format a Slack-style alert |

## Setup (2 minutes)

1. `docker compose up -d` → open n8n at <http://localhost:5678>
2. **Workflows → ⋯ → Import from File** → pick a JSON from `n8n/workflows/`
3. Open the workflow, click **Inactive → Active**
4. Copy the **Production webhook URL** (for 01/03)

### Wiring the API → n8n

The API notifies n8n on every new ticket. Set the webhook URL and restart:

```bash
# .env (local dev)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/new-ticket
```

In Docker this is already pointed at the n8n service; just make sure workflow 01 is **Active**.

### Test it end-to-end

```bash
# 1. Create an urgent ticket
curl -X POST localhost:8000/api/v1/tickets \
  -H 'Content-Type: application/json' \
  -d '{"subject":"Stranded after cancellation","message":"My flight AI860 was cancelled and I am stranded at the airport with a medical issue.","customer_name":"Test"}'

# 2. Check n8n Executions tab → workflow 01 ran → ticket escalated
curl localhost:8000/api/v1/tickets/1
```

### Extending (great portfolio commits)

- Add a real **Slack / Telegram / email** node after `Format Alert` in workflow 03
- Add a **Google Sheets / Postgres** node to log every triage decision
- Add a **daily 9 AM digest** workflow that posts `GET /tickets/stats/summary` to the team channel
