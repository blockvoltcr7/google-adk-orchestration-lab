#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"
terraform_dir="${project_root}/infra/terraform"

if [[ ! -f "${terraform_dir}/main.tf" ]]; then
  echo "Terraform root not found: ${terraform_dir}" >&2
  exit 1
fi

terraform -chdir="${terraform_dir}" init
terraform -chdir="${terraform_dir}" validate
terraform -chdir="${terraform_dir}" plan -out=tfplan
terraform -chdir="${terraform_dir}" apply tfplan
"${script_dir}/seed.sh"
"${script_dir}/verify.sh"
