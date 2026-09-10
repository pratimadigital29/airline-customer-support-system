"""Inbound webhooks: n8n workflow callbacks + customer feedback intake."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket
from app.schemas import FeedbackIn, WebhookEvent
from app.services.triage import detect_sentiment

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/n8n/ticket-event")
def n8n_ticket_event(event: WebhookEvent, db: Session = Depends(get_db)):
    """Lets n8n workflows act on tickets (escalate / assign / resolve / close)."""
    ticket = db.get(Ticket, event.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    action = event.action.lower()
    if action == "escalate":
        ticket.priority = "urgent"
        ticket.status = "pending"
        ticket.assignee = event.assignee or "duty-manager"
    elif action == "assign":
        ticket.assignee = event.assignee or "support-agent"
        ticket.status = "pending"
    elif action == "resolve":
        ticket.status = "resolved"
    elif action == "close":
        ticket.status = "closed"

    if event.note:
        ticket.message = f"{ticket.message}\n\n[n8n note] {event.note}"
    db.commit()
    return {"ok": True, "ticket_id": ticket.id, "status": ticket.status, "priority": ticket.priority}


@router.post("/feedback")
def feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    """Scores feedback; poor ratings auto-escalate the linked ticket."""
    sentiment, score = detect_sentiment(payload.comment or "")
    escalated = False
    if payload.rating <= 2:
        sentiment = "negative"
        if payload.ticket_id:
            ticket = db.get(Ticket, payload.ticket_id)
            if ticket:
                ticket.priority = "urgent"
                ticket.status = "open"
                ticket.assignee = "duty-manager"
                db.commit()
                escalated = True
    return {"sentiment": sentiment, "score": score, "escalated": escalated}
