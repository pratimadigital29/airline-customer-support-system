"""Rule-based triage: intent classification, sentiment, priority + SLA.

Production systems would call an LLM classifier here; this deterministic layer
is the fallback AND the unit-testable contract. The LLM service only *drafts*
replies — routing decisions stay explainable. That separation is intentional
and worth talking about in interviews.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.config import get_settings

INTENT_KEYWORDS: dict[str, list[str]] = {
    "flight_status": ["flight status", "where is my flight", "delayed", "delay", "on time", "departure time", "arrival time", "gate", "terminal"],
    "booking_lookup": ["pnr", "booking", "reservation", "my ticket", "itinerary", "seat number", "my flight"],
    "booking_change": ["reschedule", "change my flight", "change booking", "modify", "date change", "rebook"],
    "cancellation": ["cancel", "cancellation", "cancelled", "canceled"],
    "refund": ["refund", "money back", "chargeback", "compensation", "claim"],
    "baggage": ["baggage", "luggage", "bag ", "suitcase", "lost bag", "cabin bag", "check-in bag", "allowance", "extra bag"],
    "checkin": ["check in", "check-in", "boarding pass", "web checkin", "web check-in"],
    "complaint": ["complaint", "rude", "terrible", "worst", "horrible", "never again", "formal complaint", "manager", "supervisor"],
    "human_handoff": ["human", "real person", "agent", "call me", "talk to someone", "customer care number", "phone number", "escalate"],
    "feedback": ["feedback", "review", "rating", "survey", "suggestion"],
}

URGENT_KEYWORDS = [
    "stranded", "missed connection", "medical", "emergency", "wheelchair",
    "unaccompanied minor", "flight today", "flight is today", "leaving in",
    "cancelled and", "stranded at", "stuck at the airport",
]

HIGH_KEYWORDS = [
    "missed", "denied boarding", "overbooked", "lost baggage", "lost bag",
    "urgent", "asap", "immediately", "tomorrow", "today",
]

NEGATIVE_WORDS = [
    "angry", "furious", "terrible", "horrible", "worst", "awful", "pathetic",
    "disgusting", "rude", "unacceptable", "ridiculous", "hate", "never again",
    "complaint", "refund", "cancel", "delayed", "missed", "lost", "stuck",
    "stranded", "worried", "anxious",
]

POSITIVE_WORDS = [
    "thank", "thanks", "great", "awesome", "excellent", "wonderful", "amazing",
    "love", "appreciate", "perfect", "helpful", "quick", "fast resolution",
]

_PNR_RE = re.compile(r"\b([A-Z0-9]{6})\b")
_PNR_STOPWORDS = {
    "PLEASE", "THANKS", "THANK", "FLIGHT", "TICKET", "CANCEL", "REFUND",
    "CHANGE", "STATUS", "BAGGAGE", "MOBILE", "NUMBER", "MYSELF",
}
_FLIGHT_RE = re.compile(r"\b([A-Z0-9]{2})\s?-?\s?(\d{2,4})\b")


@dataclass
class TriageResult:
    intent: str
    confidence: float
    priority: str
    sentiment: str
    sentiment_score: float
    sla_minutes: int


def classify_intent(text: str) -> tuple[str, float]:
    """Keyword-overlap intent classifier. Returns (intent, confidence 0..1)."""
    lowered = f" {text.lower()} "
    best_intent, best_hits = "general", 0
    for intent, keywords in INTENT_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in lowered)
        if hits > best_hits:
            best_intent, best_hits = intent, hits
    if best_hits == 0:
        return "general", 0.25
    confidence = min(0.55 + 0.15 * best_hits, 0.97)
    return best_intent, round(confidence, 2)


def detect_sentiment(text: str) -> tuple[str, float]:
    """Lexicon sentiment in [-1, 1]. Negative < -0.15, positive > 0.25."""
    lowered = text.lower()
    neg = sum(1 for w in NEGATIVE_WORDS if w in lowered)
    pos = sum(1 for w in POSITIVE_WORDS if w in lowered)
    total = neg + pos
    if total == 0:
        return "neutral", 0.0
    score = round((pos - neg) / total, 2)
    if score <= -0.15:
        return "negative", score
    if score >= 0.25:
        return "positive", score
    return "neutral", score


def score_priority(text: str, intent: str, sentiment: str) -> str:
    lowered = text.lower()
    if any(k in lowered for k in URGENT_KEYWORDS):
        return "urgent"
    if intent in {"complaint", "human_handoff"} and sentiment == "negative":
        return "high"
    if any(k in lowered for k in HIGH_KEYWORDS):
        return "high"
    if intent in {"cancellation", "refund", "booking_change"}:
        return "normal"
    if sentiment == "positive" or intent == "feedback":
        return "low"
    return "normal"


def sla_for_priority(priority: str) -> int:
    settings = get_settings()
    return {
        "urgent": settings.sla_minutes_urgent,
        "high": settings.sla_minutes_high,
    }.get(priority, settings.sla_minutes_normal)


def triage(subject: str, message: str) -> TriageResult:
    text = f"{subject}\n{message}".strip()
    intent, confidence = classify_intent(text)
    sentiment, sentiment_score = detect_sentiment(text)
    priority = score_priority(text, intent, sentiment)
    return TriageResult(
        intent=intent,
        confidence=confidence,
        priority=priority,
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        sla_minutes=sla_for_priority(priority),
    )


def extract_pnr(text: str) -> str:
    """Best-effort PNR finder: 6-char code with ≥1 digit and ≥2 letters."""
    for match in _PNR_RE.finditer(text.upper()):
        code = match.group(1)
        if code in _PNR_STOPWORDS:
            continue
        letters = sum(c.isalpha() for c in code)
        digits = sum(c.isdigit() for c in code)
        if digits >= 1 and letters >= 2:
            return code
    return ""


def extract_flight_no(text: str) -> str:
    """Normalises 'AI 202', 'AI-202', '6E 234' -> 'AI202', '6E234'."""
    match = _FLIGHT_RE.search(text.upper())
    if not match:
        return ""
    return f"{match.group(1)}{match.group(2)}"
