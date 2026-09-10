"""Database models."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Ticket(Base):
    """A customer support ticket with AI triage attached."""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(255), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    customer_name: Mapped[str] = mapped_column(String(120), default="")
    customer_email: Mapped[str] = mapped_column(String(255), default="")
    pnr: Mapped[str] = mapped_column(String(16), default="")
    flight_no: Mapped[str] = mapped_column(String(16), default="")

    intent: Mapped[str] = mapped_column(String(64), default="general")
    intent_confidence: Mapped[float] = mapped_column(default=0.0)
    priority: Mapped[str] = mapped_column(String(16), default="normal")  # low|normal|high|urgent
    sentiment: Mapped[str] = mapped_column(String(16), default="neutral")
    status: Mapped[str] = mapped_column(String(16), default="open")  # open|pending|resolved|closed
    assignee: Mapped[str] = mapped_column(String(120), default="unassigned")
    suggested_reply: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
