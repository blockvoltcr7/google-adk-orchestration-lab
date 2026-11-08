# Validation Plan

## Infrastructure

1. Run `terraform init`, `terraform validate`, and `terraform plan`.
2. Apply the reviewed plan and seed the table.
3. Run `scripts/verify.sh`; require nonzero rows and a 2024-only date range.
4. Run `scripts/cleanup.sh` without `--execute`; require a successful destroy
   preview and no deletion.

## Code and runtime

1. Run `agents-cli lint`.
2. Run `uv run pytest tests/unit tests/integration`.
3. Run a local `agents-cli run` question and inspect the trace for
   `execute_sql` followed by a grounded answer.

## Behavioral evaluation

1. Run `agents-cli eval generate` on the retail eval dataset.
2. Run `agents-cli eval grade` with response quality and deterministic BigQuery
   tool-grounding metrics.
3. Inspect the result JSON and HTML. Fix the agent, not the thresholds, if a
   case fails.

## Completion evidence

- Terraform apply output and state list.
- BigQuery verification output with row count and date bounds.
- Local runtime trace.
- Test output.
- ADK eval traces and grade results.
- Successful cleanup preview with the dataset still present afterward.
