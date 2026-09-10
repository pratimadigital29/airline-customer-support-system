"""LLM client with graceful degradation: OpenAI -> Ollama -> mock templates.

Design notes (good interview material):
- Routing/triage NEVER depends on the LLM, so a provider outage degrades
  reply quality, not system correctness.
- Every provider call has a short timeout and falls back to templates.
- Prompts are built from retrieved FAQs + booking/flight facts to ground
  the answer and reduce hallucination.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are AeroServe, a warm, concise airline customer-support agent. "
    "Answer in under 120 words, use the provided facts only, never invent "
    "flight times or policies. If facts are missing, say what you need "
    "(e.g. the 6-character PNR). End with one clear next step."
)

_INTENT_INTROS = {
    "flight_status": "Thanks for sharing your flight details — here's the latest I have.",
    "booking_lookup": "I found your booking — here are the details.",
    "booking_change": "I can help with changing your booking.",
    "cancellation": "I'm sorry you need to cancel — here's how it works.",
    "refund": "Let me explain the refund process for your case.",
    "baggage": "Here's the baggage information you need.",
    "checkin": "Here's how check-in works for your flight.",
    "complaint": "I'm really sorry about this experience — your feedback matters and I've flagged it for review.",
    "human_handoff": "Of course — I'll get a human agent involved right away.",
    "feedback": "Thank you for the feedback — it genuinely helps us improve.",
    "general": "Thanks for reaching out — here's what I can do for you.",
}


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    # -- public API -----------------------------------------------------
    def draft_reply(
        self,
        *,
        intent: str,
        message: str,
        faqs: list[dict[str, Any]] | None = None,
        booking: dict[str, Any] | None = None,
        flight: dict[str, Any] | None = None,
        customer_name: str = "",
    ) -> str:
        """Draft a support reply, trying the configured provider first."""
        provider = self.settings.llm_provider.lower()
        try:
            if provider == "openai" and self.settings.openai_api_key:
                return self._openai_reply(intent, message, faqs, booking, flight, customer_name)
            if provider == "ollama":
                return self._ollama_reply(intent, message, faqs, booking, flight, customer_name)
        except Exception:  # noqa: BLE001 — fallback is the feature
            logger.warning("LLM provider '%s' failed, using template fallback", provider, exc_info=True)
        return self._template_reply(intent, message, faqs, booking, flight, customer_name)

    def summarize(self, text: str) -> str:
        """One-line summary for dashboards / Slack alerts. Template-based on purpose."""
        clean = " ".join(text.split())
        return clean[:160] + ("…" if len(clean) > 160 else "")

    # -- providers ------------------------------------------------------
    def _grounding_block(
        self,
        faqs: list[dict[str, Any]] | None,
        booking: dict[str, Any] | None,
        flight: dict[str, Any] | None,
    ) -> str:
        parts: list[str] = []
        if flight:
            parts.append(
                "Flight {flight_no} ({airline}) {origin}->{destination}, dep {departure}, "
                "arr {arrival}, status {status}, gate {gate} {terminal}.".format(**flight)
            )
        if booking:
            parts.append(
                "Booking {pnr} for {passenger}: flight {flight_no} on {date}, "
                "seat {seat} ({cabin}), status {status}.".format(**booking)
            )
        for faq in faqs or []:
            parts.append(f"Policy — {faq['question']}: {faq['answer']}")
        return "\n".join(parts) if parts else "No verified facts available."

    def _openai_reply(self, intent, message, faqs, booking, flight, customer_name) -> str:
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Customer: {customer_name or 'guest'}\nIntent: {intent}\n"
                        f"Facts:\n{self._grounding_block(faqs, booking, flight)}\n\n"
                        f"Customer message: {message}"
                    ),
                },
            ],
            "max_tokens": 300,
            "temperature": 0.4,
        }
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()

    def _ollama_reply(self, intent, message, faqs, booking, flight, customer_name) -> str:
        payload = {
            "model": self.settings.ollama_model,
            "system": SYSTEM_PROMPT,
            "prompt": (
                f"Customer: {customer_name or 'guest'}\nIntent: {intent}\n"
                f"Facts:\n{self._grounding_block(faqs, booking, flight)}\n\n"
                f"Customer message: {message}\n\nReply:"
            ),
            "stream": False,
        }
        with httpx.Client(timeout=60) as client:
            resp = client.post(f"{self.settings.ollama_base_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "").strip()

    # -- mock fallback --------------------------------------------------
    def _template_reply(self, intent, message, faqs, booking, flight, customer_name) -> str:
        greeting = f"Hi {customer_name}!" if customer_name else "Hi there!"
        intro = _INTENT_INTROS.get(intent, _INTENT_INTROS["general"])
        lines = [f"{greeting} {intro}"]

        if flight:
            lines.append(
                "✈️ Flight {flight_no} ({airline}): {origin} → {destination}, "
                "departs {departure}, arrives {arrival}. Status: {status} "
                "(Gate {gate}, {terminal}).".format(**flight)
            )
        if booking:
            lines.append(
                "🎫 Booking {pnr} for {passenger}: flight {flight_no} on {date}, "
                "seat {seat} ({cabin}). Status: {status}.".format(**booking)
            )
        for faq in faqs or []:
            lines.append(f"📌 {faq['question']}: {faq['answer']}")

        if intent == "human_handoff":
            lines.append("I've created a priority ticket and an agent will contact you shortly. Anything else I should add to it?")
        elif intent in {"cancellation", "refund", "booking_change"}:
            lines.append("Share your 6-character PNR (e.g. ABC123) and I'll pull up your booking to take this further.")
        elif not faqs and not flight and not booking:
            lines.append("Could you share your 6-character PNR or flight number (e.g. AI202)? That lets me give you exact details.")
        else:
            lines.append("Let me know if you'd like me to raise a ticket for a human agent to follow up.")
        return "\n\n".join(lines)


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
