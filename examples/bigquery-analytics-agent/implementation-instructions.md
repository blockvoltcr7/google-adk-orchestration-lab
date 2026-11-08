# Implementation Instructions

## Prerequisites

- Authenticated Google Cloud CLI and Application Default Credentials.
- Google Cloud project `your-gcp-project-id` with billing and BigQuery enabled.
- Terraform, `bq`, `uv`, and `agents-cli` installed.

## Provision and seed

```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
./scripts/provision.sh
```

Terraform creates only the disposable dataset. The seed script materializes the
2024 retail table from a Google-hosted public BigQuery dataset and limits seed
query billing to 100 MiB.

## Local agent

The scaffolded `app/agent.py` defines a stateful ADK `App`, Gemini agent, and
Google's built-in `BigQueryToolset`. Application Default Credentials authenticate
the database reader. `WriteMode.BLOCKED` and `maximum_bytes_billed` provide
execution guardrails.

For environments that standardize all database access through MCP, Google's
[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an
alternative registration path. This prototype uses ADK's native BigQuery
toolset because it is first-party, smaller, and already supports read-only and
cost controls.

## Run locally

```bash
agents-cli install
agents-cli run "Which product category had the highest completed revenue in 2024?"
```

## Cleanup

```bash
./scripts/cleanup.sh
```

The default command creates and displays a Terraform destroy plan only. After
review, `./scripts/cleanup.sh --execute` applies that exact plan. Do not run the
execute form while the demo should remain available.
