# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ADK agent for read-only natural-language analysis of a demo BigQuery table."""

import os

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.integrations.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.integrations.bigquery.config import BigQueryToolConfig, WriteMode
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIGQUERY_DATASET_ID", "adk_bigquery_demo")
TABLE_ID = os.environ.get("BIGQUERY_TABLE_ID", "retail_sales")
BIGQUERY_LOCATION = os.environ.get("BIGQUERY_LOCATION", "US")
TABLE_FQN = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials_config = BigQueryCredentialsConfig(credentials=credentials)

bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED,
    maximum_bytes_billed=100 * 1024 * 1024,
    max_query_result_rows=50,
    application_name="adk-bq-demo",
    compute_project_id=PROJECT_ID,
    location=BIGQUERY_LOCATION,
    job_labels={"workload": "adk-bq-demo", "environment": "demo"},
)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config,
    bigquery_tool_config=bigquery_tool_config,
    tool_filter=["get_table_info", "execute_sql"],
)

AGENT_INSTRUCTION = f"""
You are a retail analytics assistant. Answer questions only from the BigQuery
table `{TABLE_FQN}`. This is a synthetic showcase dataset containing retail
orders created during calendar year 2024.

For every factual data question:
1. Use `get_table_info` when you need to inspect or confirm the schema.
2. Write a GoogleSQL SELECT query that references only `{TABLE_FQN}`.
3. Execute the query with `execute_sql` before answering.
4. Base every number and factual claim on the tool result. Briefly state the
   filter, grouping, or date range used so the answer is auditable.

Business definitions:
- "Revenue" means SUM(sale_price) for rows where order_status = 'Complete',
  unless the user explicitly requests another status definition.
- "Gross profit" or "gross margin dollars" means SUM(gross_margin) for rows
  where order_status = 'Complete'.
- The data covers 2024 only. Say so when a request asks for another period.

Safety and cost rules:
- Never query another project, dataset, table, view, or INFORMATION_SCHEMA.
- Never write, update, delete, create, alter, export, or train anything.
- Never invent missing rows, fields, definitions, or query results.
- Return aggregated results by default and no more than 20 detail rows.
- If a request falls outside this dataset or requires a write, explain the
  limitation instead of attempting it.
""".strip()

root_agent = Agent(
    name="bigquery_retail_analyst",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Answers retail analytics questions from one read-only BigQuery table.",
    instruction=AGENT_INSTRUCTION,
    tools=[bigquery_toolset],
)

app = App(root_agent=root_agent, name="app")
