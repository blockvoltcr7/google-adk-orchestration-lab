"""Sequential pipeline graph nodes."""

import json
from typing import Any
from google.adk.events import Event, EventActions
from app.models import (
    OrderInput,
    ValidatedOrder,
    OrderWithFinancials,
    OrderConfirmation,
)


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
        raise ValueError(f"Could not parse valid JSON order payload from input: {text}")


def validate_order(node_input: Any) -> Event:
    """Stage 1: Ingest, validate schema, calculate line-item subtotal."""
    data = _parse_input(node_input)
    order_in = OrderInput.model_validate(data)
    subtotal = sum(item.quantity * item.unit_price for item in order_in.items)
    order_id = f"ORD-{abs(hash(order_in.customer_email)) % 100000:05d}"

    validated = ValidatedOrder(
        order_id=order_id,
        customer_name=order_in.customer_name,
        customer_email=order_in.customer_email,
        items=order_in.items,
        subtotal=round(subtotal, 2),
    )
    dumped = validated.model_dump()
    return Event(
        output=dumped,
        actions=EventActions(
            state_delta={
                "order_id": order_id,
                "customer_email": order_in.customer_email,
                "subtotal": validated.subtotal,
            }
        ),
    )


def calculate_financials(node_input: dict[str, Any]) -> Event:
    """Stage 2: Calculate tax, apply shipping rules, determine grand total."""
    subtotal = float(node_input["subtotal"])
    tax = round(subtotal * 0.0825, 2)
    shipping = 0.0 if subtotal >= 100.0 else 15.0
    grand_total = round(subtotal + tax + shipping, 2)

    financials = OrderWithFinancials(
        order_id=node_input["order_id"],
        customer_name=node_input["customer_name"],
        customer_email=node_input["customer_email"],
        subtotal=subtotal,
        tax=tax,
        shipping_fee=shipping,
        grand_total=grand_total,
    )
    dumped = financials.model_dump()
    return Event(
        output=dumped,
        actions=EventActions(
            state_delta={
                "tax": tax,
                "shipping_fee": shipping,
                "grand_total": grand_total,
            }
        ),
    )


def generate_invoice(node_input: dict[str, Any]) -> Event:
    """Stage 3: Generate formal invoice record."""
    inv_num = f"INV-{node_input['order_id']}-2026"
    invoice_record = {
        **node_input,
        "invoice_number": inv_num,
        "invoice_status": "GENERATED",
    }
    return Event(
        output=invoice_record,
        actions=EventActions(
            state_delta={"invoice_number": inv_num, "invoice_status": "GENERATED"}
        ),
    )


def dispatch_confirmation(node_input: dict[str, Any]) -> OrderConfirmation:
    """Stage 4: Produce terminal order confirmation."""
    return OrderConfirmation(
        order_id=node_input["order_id"],
        invoice_number=node_input["invoice_number"],
        customer_name=node_input["customer_name"],
        customer_email=node_input["customer_email"],
        grand_total=node_input["grand_total"],
        status="CONFIRMED",
        message=(
            f"Thank you {node_input['customer_name']}. Your order {node_input['order_id']} "
            f"has been confirmed for a total of ${node_input['grand_total']:.2f}. "
            f"Invoice {node_input['invoice_number']} sent to {node_input['customer_email']}."
        ),
    )
