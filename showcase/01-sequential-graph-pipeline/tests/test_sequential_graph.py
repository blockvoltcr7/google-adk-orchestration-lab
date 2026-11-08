"""Unit and end-to-end tests for the sequential order fulfillment graph."""

import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import Workflow
from google.genai import types

from app.agent import root_agent
from app.nodes import (
    validate_order,
    calculate_financials,
    generate_invoice,
    dispatch_confirmation,
)


def test_graph_topology():
    """Verify that root_agent is a valid Workflow with 4 sequential edges."""
    assert isinstance(root_agent, Workflow)
    assert root_agent.name == "order_fulfillment_graph"
    edges = [
        (e.from_node.name, e.route, e.to_node.name)
        for e in root_agent.graph.edges
    ]
    expected = [
        ("__START__", None, "validate_order"),
        ("validate_order", None, "calculate_financials"),
        ("calculate_financials", None, "generate_invoice"),
        ("generate_invoice", None, "dispatch_confirmation"),
    ]
    assert edges == expected


def test_calculate_financials_shipping_threshold():
    """Verify $15 shipping applied under $100 and free shipping over $100."""
    under_input = {
        "order_id": "ORD-001",
        "customer_name": "Alice",
        "customer_email": "alice@example.com",
        "subtotal": 50.0,
    }
    event_under = calculate_financials(under_input)
    assert event_under.output["shipping_fee"] == 15.0
    assert event_under.output["grand_total"] == round(50.0 + 50.0 * 0.0825 + 15.0, 2)

    over_input = {
        "order_id": "ORD-002",
        "customer_name": "Bob",
        "customer_email": "bob@example.com",
        "subtotal": 120.0,
    }
    event_over = calculate_financials(over_input)
    assert event_over.output["shipping_fee"] == 0.0
    assert event_over.output["grand_total"] == round(120.0 + 120.0 * 0.0825, 2)


def test_full_graph_execution():
    """Execute root_agent workflow from START to terminal confirmation."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(app_name="test_app", user_id="user_1")
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="test_app",
    )

    payload = (
        '{"customer_name": "Jane Doe", "customer_email": "jane@example.com", '
        '"items": [{"name": "Running Shoes", "quantity": 1, "unit_price": 110.0}]}'
    )
    content = types.Content(role="user", parts=[types.Part.from_text(text=payload)])

    events = list(
        runner.run(
            new_message=content,
            user_id="user_1",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )

    assert len(events) > 0
    # Final terminal event from dispatch_confirmation
    outputs = [e.output for e in events if e.output]
    assert len(outputs) > 0
    final_output = outputs[-1]
    assert final_output["status"] == "CONFIRMED"
    assert "Jane Doe" in final_output["customer_name"]
    assert "INV-" in final_output["invoice_number"]
    assert final_output["grand_total"] > 110.0
