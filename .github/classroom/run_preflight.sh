#!/usr/bin/env bash

set -euo pipefail

current_branch="${GITHUB_REF_NAME:-$(git branch --show-current)}"

bash .github/classroom/check_required_files.sh
bash .github/classroom/check_forbidden_files.sh
bash .github/classroom/check_agents_contract.sh
bash .github/classroom/check_feedback_guidance.sh

case "$current_branch" in
  integracion-01)
    python3 .github/classroom/check_iteration_outputs.py integracion-01
    ;;
  integracion-02)
    python3 .github/classroom/check_iteration_outputs.py integracion-02
    ;;
  *)
    python3 .github/classroom/check_iteration_outputs.py starter
    ;;
esac

printf 'Preflight de %s: OK\n' "$current_branch"

