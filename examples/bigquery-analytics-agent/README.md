# BigQuery Retail Analytics Agent

A local Google ADK showcase that translates natural-language retail questions
into read-only BigQuery queries. It uses Google's supported `BigQueryToolset`, a
small Terraform-managed dataset, and Agents CLI behavioral evaluations.

## What the demo answers

- Total completed revenue in 2024
- Top categories or countries by revenue and gross profit
- Acquisition traffic-source comparisons
- Order-status, brand, department, and customer-demographic summaries

The source is Google's synthetic
`bigquery-public-data.thelook_ecommerce` dataset. The materialized table keeps
only analytic fields and excludes names, email, and street addresses.

## Architecture and safety

- One ADK agent and one denormalized BigQuery table
- BigQuery writes blocked through `WriteMode.BLOCKED`
- Query billing capped at 100 MiB per tool call
- Results capped at 50 rows
- Dataset and jobs labeled for cost/audit discovery
- Dataset tables expire after 30 days unless refreshed

BigQuery is serverless; there is no database instance to stop. Cleanup means
destroying the Terraform-managed demo dataset.

## Setup

```bash
agents-cli install
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
# Set project_id in terraform.tfvars to your own Google Cloud project ID.
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"  # Replace with the same ID.
./scripts/provision.sh
```

The provision script initializes and applies Terraform, seeds the 2024 table,
and prints verification statistics.

## Run locally

```bash
agents-cli run "Which product category had the highest completed revenue in 2024?"
```

For an interactive browser session:

```bash
agents-cli playground
```

## Test and evaluate

```bash
agents-cli lint
uv run pytest tests/unit tests/integration
agents-cli eval run \
  --dataset tests/eval/datasets/bigquery-retail.json \
  --config tests/eval/eval_config.yaml \
  --output artifacts/grade_results/bigquery-retail \
  --project your-gcp-project-id \
  --region us-east1 \
  --concurrency 2
```

The eval suite checks grounded retail answers, query-tool use, and refusal of a
table-deletion request.

## Cleanup without surprises

Preview only:

```bash
./scripts/cleanup.sh
```

After inspecting the destroy plan, execute it explicitly:

```bash
./scripts/cleanup.sh --execute
```

The execute form deletes the demo dataset and tables. It does not disable the
BigQuery API.

## Design records

- [Agent specification](.agents-cli-spec.md)
- [Solution architecture](solution-architecture.md)
- [BigQuery versus Cloud SQL and cost notes](cost-and-service-notes.md)
- [Implementation instructions](implementation-instructions.md)
- [Validation plan](validation-plan.md)
