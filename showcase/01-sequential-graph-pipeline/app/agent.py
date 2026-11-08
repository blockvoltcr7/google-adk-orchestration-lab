"""ADK Composition root for the sequential order fulfillment graph."""

from google.adk.apps import App
from google.adk.workflow import Workflow, START
from app.nodes import (
    validate_order,
    calculate_financials,
    generate_invoice,
    dispatch_confirmation,
)

root_agent = Workflow(
    name="order_fulfillment_graph",
    description="Deterministic sequential graph pipeline for e-commerce order processing",
    edges=[
        (START, validate_order),
        (validate_order, calculate_financials),
        (calculate_financials, generate_invoice),
        (generate_invoice, dispatch_confirmation),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
