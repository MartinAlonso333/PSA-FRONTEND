#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

required_files=(
  "AGENTS.md"
  "README.md"
  "index.html"
  "styles.css"
  "app.js"
  "config.json"
  "config.example.json"
  "scripts/dev-server.sh"
  "scripts/smoke-mvp.sh"
  "scripts/smoke_mvp.py"
  "scripts/preflight-integracion-01.sh"
  "scripts/preflight-integracion-02.sh"
  "iteraciones/README.md"
  "iteraciones/integracion-01.md"
  "iteraciones/integracion-02.md"
  "entregas/README.md"
  "entregas/integracion-01-template.md"
  "entregas/integracion-02-template.md"
  "docs/vision/vision-tribu-template.md"
  "docs/analisis/modelo-dominio-template.md"
  "docs/analisis/modelo-dominio-template.puml"
  "docs/arquitectura/api-integracion-template.md"
  "docs/operacion/guia-tribu-template.md"
  ".github/workflows/classroom.yml"
  ".github/classroom/run_preflight.sh"
  ".github/classroom/check_required_files.sh"
  ".github/classroom/check_forbidden_files.sh"
  ".github/classroom/check_agents_contract.sh"
  ".github/classroom/check_feedback_guidance.sh"
  ".github/classroom/check_iteration_outputs.py"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "$path" ]]; then
    printf 'missing required file: %s\n' "$path" >&2
    exit 1
  fi
done
