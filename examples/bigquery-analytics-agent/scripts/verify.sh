#!/usr/bin/env bash
set -euo pipefail

project_id="${GOOGLE_CLOUD_PROJECT:-your-gcp-project-id}"
dataset_id="${BIGQUERY_DATASET_ID:-adk_bigquery_demo}"
table_id="${BIGQUERY_TABLE_ID:-retail_sales}"
location="${BIGQUERY_LOCATION:-US}"

if [[ ! "${project_id}" =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ ]]; then
  echo "Invalid GOOGLE_CLOUD_PROJECT: ${project_id}" >&2
  exit 1
fi
if (( ${#dataset_id} > 1024 )) || [[ ! "${dataset_id}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "Invalid BIGQUERY_DATASET_ID: ${dataset_id}" >&2
  exit 1
fi
if (( ${#table_id} > 1024 )) || [[ ! "${table_id}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "Invalid BIGQUERY_TABLE_ID: ${table_id}" >&2
  exit 1
fi
if [[ "${location}" != "US" ]]; then
  echo "BIGQUERY_LOCATION must be US for the selected public dataset." >&2
  exit 1
fi

table_fqn="${project_id}.${dataset_id}.${table_id}"
bq \
  --project_id="${project_id}" \
  --location="${location}" \
  query \
  --use_legacy_sql=false \
  --maximum_bytes_billed=104857600 \
  --format=prettyjson \
  "SELECT COUNT(*) AS row_count, MIN(DATE(order_created_at)) AS first_date, MAX(DATE(order_created_at)) AS last_date, ROUND(SUM(IF(order_status = 'Complete', sale_price, 0)), 2) AS completed_revenue FROM \`${table_fqn}\`"
