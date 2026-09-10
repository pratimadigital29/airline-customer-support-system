"""Conversational support endpoint (powers the demo chat UI)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ticket
from app.schemas import ChatRequest, ChatResponse
from app.services import knowledge
from app.services.llm import get_llm_client
from app.services.triage import extract_flight_no, extract_pnr, triage

router = APIRouter(prefix="/chat", tags=["chat"])

_HUMAN_PHRASES = ("human", "real person", "agent", "call me", "talk to someone", "escalate", "supervisor", "manager")


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    message = payload.message.strip()
    result = triage("", message)

    pnr = payload.pnr.strip().upper() or extract_pnr(message)
    flight_no = extract_flight_no(message)
    booking = knowledge.get_booking(pnr) if pnr else None
    flight = knowledge.get_flight(flight_no) if flight_no else None
    if booking and not flight:
        flight = knowledge.get_flight(booking["flight_no"])
    faqs = knowledge.search_faqs(message)

    sources = [f"faq:{f['id']} {f['question']}" for f in faqs]
    actions: list[dict] = []
    if booking:
        actions.append({"type": "booking_lookup", "pnr": booking["pnr"]})
    if flight:
        actions.append({"type": "flight_lookup", "flight_no": flight["flight_no"]})

    wants_human = any(p in message.lower() for p in _HUMAN_PHRASES)
    ticket_id: int | None = None

    if wants_human or (result.priority == "urgent" and result.intent in {"complaint", "cancellation", "refund"}):
        ticket = Ticket(
            subject=message[:120],
            message=message,
            customer_name=payload.customer_name,
            pnr=pnr,
            flight_no=flight["flight_no"] if flight else flight_no,
            intent=result.intent,
            intent_confidence=result.confidence,
            priority="urgent" if result.priority == "urgent" else "high",
            sentiment=result.sentiment,
            assignee="human-queue",
            suggested_reply="",
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        ticket_id = ticket.id
        actions.append({"type": "ticket_created", "ticket_id": ticket_id})

    reply = get_llm_client().draft_reply(
        intent="human_handoff" if ticket_id else result.intent,
        message=message,
        faqs=faqs,
        booking=booking,
        flight=flight,
        customer_name=payload.customer_name,
    )
    if ticket_id:
        reply = f"🎟️ I've raised priority ticket **#{ticket_id}** for a human agent.\n\n{reply}"

    return ChatResponse(
        reply=reply,
        intent=result.intent,
        confidence=result.confidence,
        sentiment=result.sentiment,
        sources=sources,
        actions=actions,
        ticket_id=ticket_id,
    )
