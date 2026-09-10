"""Unit tests for the deterministic triage contract."""

from app.services.triage import (
    classify_intent,
    detect_sentiment,
    extract_flight_no,
    extract_pnr,
    triage,
)


def test_refund_intent():
    intent, conf = classify_intent("Where is my refund? I want my money back for the ticket.")
    assert intent == "refund"
    assert conf > 0.5


def test_baggage_intent():
    intent, _ = classify_intent("My luggage is missing since yesterday")
    assert intent == "baggage"


def test_general_fallback():
    intent, conf = classify_intent("Hello, just saying hi")
    assert intent == "general"
    assert conf < 0.5


def test_negative_sentiment():
    sentiment, score = detect_sentiment("This is terrible and unacceptable, I am furious")
    assert sentiment == "negative"
    assert score < 0


def test_positive_sentiment():
    sentiment, score = detect_sentiment("Thanks, amazing and quick help!")
    assert sentiment == "positive"
    assert score > 0


def test_urgent_priority_for_stranded():
    result = triage("Stranded", "My flight was cancelled and I am stranded at the airport")
    assert result.priority == "urgent"
    assert result.sla_minutes == 30


def test_pnr_extraction():
    assert extract_pnr("My PNR is ABC123 please help") == "ABC123"
    assert extract_pnr("no code here at all") == ""


def test_flight_extraction():
    assert extract_flight_no("status of AI 202 please") == "AI202"
    assert extract_flight_no("is 6E-234 on time?") == "6E234"
