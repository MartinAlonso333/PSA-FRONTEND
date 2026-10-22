#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

forbidden=(
  "build.gradle"
  "settings.gradle"
  "gradlew"
  "gradlew.bat"
  "gradle/"
  "db/"
  "src/main/java/"
  "src/test/java/"
)

for path in "${forbidden[@]}"; do
  if [[ -e "$path" ]]; then
    printf 'forbidden file or directory present: %s\n' "$path" >&2
    exit 1
  fi
done

