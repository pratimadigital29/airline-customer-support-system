"""Pydantic request/response contracts for the public API."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    subject: str = Field(default="", max_length=255)
    message: str = Field(..., min_length=3, max_length=5000)
    customer_name: str = Field(default="", max_length=120)
    customer_email: str = Field(default="", max_length=255)
    pnr: str = Field(default="", max_length=16)
    flight_no: str = Field(default="", max_length=16)


class TicketUpdate(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(open|pending|resolved|closed)$")
    priority: Optional[str] = Field(default=None, pattern="^(low|normal|high|urgent)$")
    assignee: Optional[str] = Field(default=None, max_length=120)


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    message: str
    customer_name: str
    customer_email: str
    pnr: str
    flight_no: str
    intent: str
    intent_confidence: float
    priority: str
    sentiment: str
    status: str
    assignee: str
    suggested_reply: str
    created_at: datetime
    updated_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    customer_name: str = Field(default="", max_length=120)
    pnr: str = Field(default="", max_length=16)


class ChatResponse(BaseModel):
    reply: str
    intent: str
    confidence: float
    sentiment: str
    sources: list[str] = []
    actions: list[dict[str, Any]] = []
    ticket_id: Optional[int] = None


class FlightOut(BaseModel):
    flight_no: str
    airline: str
    origin: str
    destination: str
    departure: str
    arrival: str
    status: str
    gate: str
    terminal: str


class BookingOut(BaseModel):
    pnr: str
    passenger: str
    flight_no: str
    date: str
    seat: str
    cabin: str
    status: str


class StatsOut(BaseModel):
    total: int
    open: int
    pending: int
    resolved: int
    by_priority: dict[str, int]
    by_intent: dict[str, int]
    sla_breached: int


class WebhookEvent(BaseModel):
    ticket_id: int
    action: str = "note"  # escalate | assign | resolve | close | note
    note: str = ""
    assignee: str = ""


class FeedbackIn(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(default="", max_length=2000)
    ticket_id: Optional[int] = None
