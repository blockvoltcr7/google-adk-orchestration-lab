#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"

project_id="${GOOGLE_CLOUD_PROJECT:-your-gcp-project-id}"
dataset_id="${BIGQUERY_DATASET_ID:-adk_bigquery_demo}"
table_id="${BIGQUERY_TABLE_ID:-retail_sales}"
location="${BIGQUERY_LOCATION:-US}"
table_retention_seconds=2592000

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

seed_sql="${project_root}/data/seed_retail_sales.sql"
if [[ ! -f "${seed_sql}" ]]; then
  echo "Seed SQL not found: ${seed_sql}" >&2
  exit 1
fi

destination="${project_id}:${dataset_id}.${table_id}"
echo "Seeding ${destination} from bigquery-public-data.thelook_ecommerce (2024 only)."

bq \
  --project_id="${project_id}" \
  --location="${location}" \
  --format=none \
  query \
  --use_legacy_sql=false \
  --destination_table="${destination}" \
  --replace \
  --time_partitioning_type=DAY \
  --time_partitioning_field=order_created_at \
  --clustering_fields=customer_country,product_category,order_status \
  --maximum_bytes_billed=104857600 \
  --label=workload:adk-bq-demo \
  < "${seed_sql}"

bq \
  --project_id="${project_id}" \
  update \
  --expiration="${table_retention_seconds}" \
  --time_partitioning_expiration=-1 \
  "${destination}"

echo "Seed complete: ${destination}"
