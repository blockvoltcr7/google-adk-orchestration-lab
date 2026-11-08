"""Nodes for enterprise ticket classification and conditional routing."""

import json
from typing import Any
from google.adk.events import Event, EventActions
from google.adk.workflow import DEFAULT_ROUTE
from app.models import TicketInput, SpecialistResolution, FinalResolutionRecord


def _parse_input(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    text = getattr(raw, "text", None)
    if text is None and hasattr(raw, "parts"):
        text = "".join(getattr(p, "text", "") or "" for p in raw.parts)
    elif not isinstance(text, str):
        text = str(raw)
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise ValueError(f"Could not parse valid JSON ticket payload from: {text}")


def triage_ticket(node_input: Any) -> Event:
    """Triage node: classifies ticket and sets the graph routing signal."""
    data = _parse_input(node_input)
    ticket = TicketInput.model_validate(data)
    content = f"{ticket.subject} {ticket.body}".lower()

    if any(k in content for k in ["refund", "invoice", "charge", "billing", "payment", "subscription"]):
        route = "billing"
    elif any(k in content for k in ["bug", "crash", "error", "exception", "api", "timeout", "latency"]):
        route = "technical"
    elif any(k in content for k in ["password", "login", "sso", "mfa", "permission", "access", "account"]):
        route = "account"
    else:
        route = DEFAULT_ROUTE

    return Event(
        output=ticket.model_dump(),
        actions=EventActions(
            route=route,
            state_delta={
                "ticket_id": ticket.ticket_id,
                "customer_id": ticket.customer_id,
                "triage_route": route,
            },
        ),
    )


def handle_billing(node_input: dict[str, Any]) -> Event:
    """Specialist node for billing inquiries."""
    resolution = SpecialistResolution(
        ticket_id=node_input["ticket_id"],
        department="Billing & Payments",
        assigned_specialist="Finance Desk Agent #402",
        action_taken="Reviewed transaction history and initiated invoice ledger audit.",
        status="INVESTIGATING",
        sla_hours=4,
    )
    return Event(
        output=resolution.model_dump(),
        actions=EventActions(state_delta={"department": resolution.department}),
    )


def handle_technical(node_input: dict[str, Any]) -> Event:
    """Specialist node for engineering and technical escalations."""
    resolution = SpecialistResolution(
        ticket_id=node_input["ticket_id"],
        department="Engineering Support",
        assigned_specialist="Site Reliability Engineer #108",
        action_taken="Captured stack trace and created priority JIRA bug ticket.",
        status="TRIAGED",
        sla_hours=2,
    )
    return Event(
        output=resolution.model_dump(),
        actions=EventActions(state_delta={"department": resolution.department}),
    )


def handle_account(node_input: dict[str, Any]) -> Event:
    """Specialist node for IAM, security, and credentials."""
    resolution = SpecialistResolution(
        ticket_id=node_input["ticket_id"],
        department="Identity & Access Security",
        assigned_specialist="Security Operations Specialist #301",
        action_taken="Triggered secure MFA reset challenge to verified email.",
        status="CHALLENGE_ISSUED",
        sla_hours=1,
    )
    return Event(
        output=resolution.model_dump(),
        actions=EventActions(state_delta={"department": resolution.department}),
    )


def handle_fallback(node_input: dict[str, Any]) -> Event:
    """Fallback handler for tickets matched by DEFAULT_ROUTE."""
    resolution = SpecialistResolution(
        ticket_id=node_input["ticket_id"],
        department="General Customer Care",
        assigned_specialist="Frontline Care Agent #001",
        action_taken="Standard intake acknowledgment and general inquiry response sent.",
        status="QUEUED",
        sla_hours=24,
    )
    return Event(
        output=resolution.model_dump(),
        actions=EventActions(state_delta={"department": resolution.department}),
    )


def format_ticket_resolution(node_input: dict[str, Any]) -> FinalResolutionRecord:
    """Terminal node synthesizing the final ticket status."""
    return FinalResolutionRecord(
        ticket_id=node_input["ticket_id"],
        department=node_input["department"],
        status=node_input["status"],
        assigned_specialist=node_input["assigned_specialist"],
        sla_hours=node_input["sla_hours"],
        resolution_summary=(
            f"Ticket {node_input['ticket_id']} routed to {node_input['department']}. "
            f"Assigned to {node_input['assigned_specialist']}. "
            f"Action: {node_input['action_taken']} Target SLA: {node_input['sla_hours']}h."
        ),
    )
