#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

grep -q '## Entregables de tribu' README.md
grep -q '## Como se trabaja' README.md
grep -q '## Verificacion rapida' README.md
! grep -qi 'GitHub Classroom' README.md
! grep -qi 'Feedback' README.md
! grep -qi 'prefijo' README.md
