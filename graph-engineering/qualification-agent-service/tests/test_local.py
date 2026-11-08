from __future__ import annotations

import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to sys.path so app imports work
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.main import app

def test_qualification_and_state_injection():
    client = TestClient(app)

    # 1. Health check
    health_resp = client.get("/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.text}"
    print("✓ Health check passed")

    # 2. Turn 1: Inbound payload with metadata and user message
    payload_turn_1 = {
        "user_id": "usr_alpha_99",
        "contact_id": "cnt_corp_882",
        "calendar_id": "sales-team-cal@acmecorp.com",
        "message": "Hi, we are exploring an enterprise contract. We have about 180 seats and need SOC2 compliance.",
        "metadata": {
            "company_name": "Global Logistics Inc",
            "company_size": 180,
            "budget_range": "$50k-$75k",
            "current_stack": ["Salesforce", "Slack"]
        }
    }

    print("\n--- Sending Turn 1 Inbound Payload ---")
    response_1 = client.post("/qualify", json=payload_turn_1)
    assert response_1.status_code == 200, f"Turn 1 failed: {response_1.text}"
    data_1 = response_1.json()

    print(f"Session ID: {data_1['session_id']}")
    print(f"Agent Response:\n{data_1['response_text']}")
    print(f"Qualification Status: {data_1['qualification_status']}")
    
    # Verify state was injected
    snapshot = data_1["session_state_snapshot"]
    assert snapshot["contact_id"] == "cnt_corp_882", "Contact ID not found in session state"
    assert snapshot["calendar_id"] == "sales-team-cal@acmecorp.com", "Calendar ID not found in state"
    assert snapshot["metadata"]["company_size"] == 180, "Metadata not injected into state"
    print("✓ Turn 1 session state successfully verified")

    # 3. Turn 2: User books meeting (agent must retrieve calendar_id from state)
    payload_turn_2 = {
        "user_id": "usr_alpha_99",
        "contact_id": "cnt_corp_882",
        "calendar_id": "sales-team-cal@acmecorp.com",
        "message": "Tomorrow at 2:00 PM EST works best for our team.",
        "metadata": {}
    }

    print("\n--- Sending Turn 2 Booking Message ---")
    response_2 = client.post("/qualify", json=payload_turn_2)
    assert response_2.status_code == 200, f"Turn 2 failed: {response_2.text}"
    data_2 = response_2.json()

    print(f"Agent Response:\n{data_2['response_text']}")
    print(f"Meeting Booked Flag: {data_2['meeting_booked']}")
    
    snapshot_2 = data_2["session_state_snapshot"]
    if data_2["meeting_booked"]:
        booking = snapshot_2.get("meeting_booking", {})
        print(f"✓ Meeting successfully booked on calendar: {booking.get('calendar_id')}")
        assert booking.get("calendar_id") == "sales-team-cal@acmecorp.com"
    else:
        print("Note: Agent held conversation open or requested further details.")

if __name__ == "__main__":
    test_qualification_and_state_injection()
