#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

grep -qi 'template starter' AGENTS.md
grep -q '2026-1c-tpg-tribu' AGENTS.md
grep -q 'interfaz web en la raiz del repositorio' AGENTS.md
grep -q 'index.html' AGENTS.md
grep -q 'styles.css' AGENTS.md
grep -q 'app.js' AGENTS.md
grep -q 'config.json' AGENTS.md
grep -q 'proceso, configuracion, verificaciones, despliegue y demo' AGENTS.md
