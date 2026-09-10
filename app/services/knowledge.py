"""Static knowledge base: FAQs, flights, bookings.

Seeded from JSON so the demo runs without external systems. In production
these become adapters to the PSS/GDS (Amadeus/Navitaire), CRM and CMS —
the function signatures are already shaped like that boundary.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> Any:
    with open(DATA_DIR / name, encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache
def faqs() -> list[dict[str, Any]]:
    return _load("faqs.json")


@lru_cache
def flights() -> list[dict[str, Any]]:
    return _load("flights.json")


@lru_cache
def bookings() -> list[dict[str, Any]]:
    return _load("bookings.json")


def _tokens(text: str) -> set[str]:
    return {t.strip(".,!?;:()\"'").lower() for t in text.split() if len(t) > 2}


def search_faqs(query: str, top_k: int = 2) -> list[dict[str, Any]]:
    """Tiny keyword-overlap retriever (stand-in for vector search)."""
    q = _tokens(query)
    if not q:
        return []
    scored: list[tuple[int, dict[str, Any]]] = []
    for faq in faqs():
        haystack = _tokens(f"{faq['question']} {faq['answer']} {faq.get('category', '')}")
        overlap = len(q & haystack)
        if overlap:
            scored.append((overlap, faq))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [faq for _, faq in scored[:top_k]]


def get_flight(flight_no: str) -> dict[str, Any] | None:
    wanted = flight_no.replace(" ", "").replace("-", "").upper()
    for flight in flights():
        if flight["flight_no"].replace(" ", "").replace("-", "").upper() == wanted:
            return flight
    return None


def search_flights(origin: str = "", destination: str = "", status: str = "") -> list[dict[str, Any]]:
    results = flights()
    if origin:
        results = [f for f in results if f["origin"].upper() == origin.upper()]
    if destination:
        results = [f for f in results if f["destination"].upper() == destination.upper()]
    if status:
        results = [f for f in results if f["status"].lower() == status.lower()]
    return results


def get_booking(pnr: str) -> dict[str, Any] | None:
    wanted = pnr.strip().upper()
    for booking in bookings():
        if booking["pnr"].upper() == wanted:
            return booking
    return None
