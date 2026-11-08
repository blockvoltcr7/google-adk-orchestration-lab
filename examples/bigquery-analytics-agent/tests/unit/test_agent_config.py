"""Deterministic tests for the BigQuery agent's safety configuration."""

import asyncio

from google.adk.integrations.bigquery.config import WriteMode

from app.agent import (
    AGENT_INSTRUCTION,
    TABLE_FQN,
    bigquery_tool_config,
    bigquery_toolset,
)


def test_bigquery_toolset_is_read_only_and_cost_bounded() -> None:
    assert bigquery_tool_config.write_mode is WriteMode.BLOCKED
    assert bigquery_tool_config.maximum_bytes_billed == 100 * 1024 * 1024
    assert bigquery_tool_config.max_query_result_rows == 50


def test_only_metadata_and_query_tools_are_exposed() -> None:
    tools = asyncio.run(bigquery_toolset.get_tools())
    assert {tool.name for tool in tools} == {"get_table_info", "execute_sql"}


def test_instruction_scopes_queries_to_demo_table() -> None:
    assert TABLE_FQN in AGENT_INSTRUCTION
    assert "Never query another project" in AGENT_INSTRUCTION
    assert "order_status = 'Complete'" in AGENT_INSTRUCTION
