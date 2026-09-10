"""Ticket CRUD + triage + dashboard stats."""

import logging
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Ticket
from app.schemas import TicketCreate, TicketOut, TicketUpdate
from app.services import knowledge
from app.services.llm import get_llm_client
from app.services.triage import extract_flight_no, extract_pnr, sla_for_priority, triage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["tickets"])


def _notify_n8n(ticket: Ticket) -> None:
    """Fire-and-forget event to n8n so workflows can orchestrate humans/tools."""
    url = get_settings().n8n_webhook_url
    if not url:
        return
    try:
        with httpx.Client(timeout=3) as client:
            client.post(url, json={
                "event": "ticket.created",
                "ticket_id": ticket.id,
                "priority": ticket.priority,
                "intent": ticket.intent,
                "sentiment": ticket.sentiment,
                "subject": ticket.subject,
                "customer_email": ticket.customer_email,
            })
    except Exception:  # noqa: BLE001 — automation must never break ticket creation
        logger.warning("n8n webhook failed for ticket %s", ticket.id, exc_info=True)


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    result = triage(payload.subject, payload.message)
    pnr = payload.pnr.strip().upper() or extract_pnr(f"{payload.subject} {payload.message}")
    flight_no = payload.flight_no.strip().upper() or extract_flight_no(f"{payload.subject} {payload.message}")

    booking = knowledge.get_booking(pnr) if pnr else None
    flight = knowledge.get_flight(flight_no) if flight_no else None
    if booking and not flight:
        flight = knowledge.get_flight(booking["flight_no"])
    faqs = knowledge.search_faqs(f"{payload.subject} {payload.message}")

    reply = get_llm_client().draft_reply(
        intent=result.intent,
        message=payload.message,
        faqs=faqs,
        booking=booking,
        flight=flight,
        customer_name=payload.customer_name,
    )

    ticket = Ticket(
        subject=payload.subject,
        message=payload.message,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        pnr=pnr,
        flight_no=flight_no,
        intent=result.intent,
        intent_confidence=result.confidence,
        priority=result.priority,
        sentiment=result.sentiment,
        suggested_reply=reply,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    _notify_n8n(ticket)
    return ticket


@router.get("/stats/summary")
def ticket_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Ticket.id)).scalar() or 0
    by_status = dict(
        db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    )
    by_priority = dict(
        db.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
    )
    by_intent = dict(
        db.query(Ticket.intent, func.count(Ticket.id)).group_by(Ticket.intent).all()
    )
    now = datetime.now(timezone.utc)
    breached = 0
    for ticket in db.query(Ticket).filter(Ticket.status.in_(["open", "pending"])).all():
        created = ticket.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if now - created > timedelta(minutes=sla_for_priority(ticket.priority)):
            breached += 1
    return {
        "total": total,
        "open": by_status.get("open", 0),
        "pending": by_status.get("pending", 0),
        "resolved": by_status.get("resolved", 0) + by_status.get("closed", 0),
        "by_priority": by_priority,
        "by_intent": by_intent,
        "sla_breached": breached,
    }


@router.get("")
def list_tickets(
    status: str = "",
    priority: str = "",
    intent: str = "",
    q: str = "",
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Ticket).order_by(Ticket.created_at.desc())
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if intent:
        query = query.filter(Ticket.intent == intent)
    if q:
        like = f"%{q}%"
        query = query.filter((Ticket.subject.like(like)) | (Ticket.message.like(like)))
    return [TicketOut.model_validate(t) for t in query.limit(min(limit, 200)).all()]


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for field in ("status", "priority", "assignee"):
        value = getattr(payload, field)
        if value:
            setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket
