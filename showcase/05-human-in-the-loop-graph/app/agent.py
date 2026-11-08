"""ADK Composition root for the human-in-the-loop expense authorization graph."""

from google.adk.apps import App
from google.adk.workflow import Workflow, START
from app.nodes import (
    assess_expense_risk,
    manager_approval_gate,
    execute_reimbursement,
    notify_rejection,
)

root_agent = Workflow(
    name="expense_authorization_graph",
    description="Human-in-the-loop approval checkpoint and risk gate graph",
    edges=[
        (START, assess_expense_risk),
        (
            assess_expense_risk,
            {
                "auto_approve": execute_reimbursement,
                "require_approval": manager_approval_gate,
            },
        ),
        (
            manager_approval_gate,
            {
                "approved": execute_reimbursement,
                "rejected": notify_rejection,
            },
        ),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
