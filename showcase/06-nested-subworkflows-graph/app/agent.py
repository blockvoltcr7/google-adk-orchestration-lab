"""ADK Composition root for the nested sub-workflows architecture."""

from google.adk.apps import App
from google.adk.workflow import Workflow, START
from app.subworkflows import (
    ingestion_subworkflow,
    editorial_subworkflow,
    distribution_subworkflow,
)

root_agent = Workflow(
    name="publishing_studio_parent_graph",
    description="Parent graph orchestrating three encapsulated sub-workflows",
    edges=[
        (START, ingestion_subworkflow),
        (ingestion_subworkflow, editorial_subworkflow),
        (editorial_subworkflow, distribution_subworkflow),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
