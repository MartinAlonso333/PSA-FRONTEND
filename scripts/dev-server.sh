#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
port="${PORT:-4173}"

cd "$repo_root"
python3 -m http.server "$port" --bind 127.0.0.1

