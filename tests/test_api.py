"""API integration tests (run against an isolated test DB)."""


def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready(client):
    assert client.get("/api/v1/ready").status_code == 200


def test_create_ticket_triages_and_drafts(client):
    resp = client.post("/api/v1/tickets", json={
        "subject": "Refund needed",
        "message": "My flight was cancelled, please refund my money urgently.",
        "customer_name": "Test User",
        "customer_email": "test@example.com",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["intent"] in {"refund", "cancellation"}
    assert body["priority"] in {"normal", "high", "urgent"}
    assert len(body["suggested_reply"]) > 50
    assert body["status"] == "open"


def test_create_ticket_extracts_pnr_and_flight(client):
    resp = client.post("/api/v1/tickets", json={
        "subject": "Booking help",
        "message": "PNR ABC123 on flight AI202, please change my seat",
        "customer_name": "Aarav",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["pnr"] == "ABC123"
    assert body["flight_no"] == "AI202"


def test_list_and_update_ticket(client):
    created = client.post("/api/v1/tickets", json={
        "subject": "Baggage query",
        "message": "What is the baggage allowance for economy?",
    }).json()
    listed = client.get("/api/v1/tickets").json()
    assert any(t["id"] == created["id"] for t in listed)

    updated = client.patch(f"/api/v1/tickets/{created['id']}", json={"status": "resolved"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "resolved"


def test_chat_booking_lookup(client):
    resp = client.post("/api/v1/chat", json={"message": "My PNR is ABC123, show my booking"})
    assert resp.status_code == 200
    body = resp.json()
    assert "AI202" in body["reply"] or "Aarav" in body["reply"]
    assert any(a["type"] == "booking_lookup" for a in body["actions"])


def test_chat_flight_status(client):
    resp = client.post("/api/v1/chat", json={"message": "What is the status of flight 6E234?"})
    assert resp.status_code == 200
    assert "6E234" in resp.json()["reply"]


def test_chat_human_handoff_creates_ticket(client):
    resp = client.post("/api/v1/chat", json={"message": "I want to talk to a human agent now"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ticket_id"] is not None


def test_flight_endpoints(client):
    assert client.get("/api/v1/flights/AI202").status_code == 200
    assert client.get("/api/v1/flights/NOPE999").status_code == 404
    assert len(client.get("/api/v1/flights?origin=DEL").json()) >= 1


def test_booking_endpoint(client):
    resp = client.get("/api/v1/bookings/ABC123")
    assert resp.status_code == 200
    assert resp.json()["passenger"] == "Aarav Sharma"
    assert client.get("/api/v1/bookings/ZZZ999").status_code == 404


def test_stats_summary(client):
    client.post("/api/v1/tickets", json={"subject": "s", "message": "refund please for cancelled flight"})
    resp = client.get("/api/v1/tickets/stats/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert "by_priority" in body


def test_feedback_escalation(client):
    created = client.post("/api/v1/tickets", json={"subject": "s", "message": "general question"}).json()
    resp = client.post("/api/v1/webhooks/feedback", json={
        "rating": 1, "comment": "terrible service", "ticket_id": created["id"],
    })
    assert resp.json()["escalated"] is True
    ticket = client.get(f"/api/v1/tickets/{created['id']}").json()
    assert ticket["priority"] == "urgent"


def test_n8n_ticket_event(client):
    created = client.post("/api/v1/tickets", json={"subject": "s", "message": "general question"}).json()
    resp = client.post("/api/v1/webhooks/n8n/ticket-event", json={
        "ticket_id": created["id"], "action": "escalate",
    })
    assert resp.status_code == 200
    assert resp.json()["priority"] == "urgent"
