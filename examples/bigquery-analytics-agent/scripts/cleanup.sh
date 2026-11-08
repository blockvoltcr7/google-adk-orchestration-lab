#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"
terraform_dir="${project_root}/infra/terraform"
execute=false

if [[ "${1:-}" == "--execute" ]]; then
  execute=true
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--execute]" >&2
  exit 1
fi

if [[ ! -d "${terraform_dir}" || ! -f "${terraform_dir}/main.tf" ]]; then
  echo "Refusing cleanup: expected Terraform root is missing: ${terraform_dir}" >&2
  exit 1
fi

echo "Terraform cleanup target: ${terraform_dir}"
terraform -chdir="${terraform_dir}" state list
terraform -chdir="${terraform_dir}" plan -destroy -out=destroy.tfplan

if [[ "${execute}" != "true" ]]; then
  echo "Cleanup preview complete. No resources were deleted."
  echo "Run $0 --execute to apply the inspected destroy plan."
  exit 0
fi

terraform -chdir="${terraform_dir}" apply destroy.tfplan
echo "Terraform-managed demo dataset removed. The BigQuery API remains enabled."
