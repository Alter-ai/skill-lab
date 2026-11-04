#!/usr/bin/env bash
# Self-check for skills/c4-architecture/scripts/render.sh (needs mmdc installed).
# Run: bash tests/test_render.sh
set -euo pipefail
render="$(cd "$(dirname "$0")/.." && pwd)/skills/c4-architecture/scripts/render.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

block='```mermaid
C4Context
  Person(user, "User", "Uses it")
  System(app, "App", "Does it")
  Rel(user, app, "Uses")
```'

printf '# One\n\n%s\n' "$block" > "$tmp/one.md"
printf '# Two\n\n## A\n%s\n\nyaml below\n\n## B\n%s\n\n```yaml\nelements: []\n```\n' "$block" "$block" > "$tmp/two.md"

# single block keeps the old name: one.png
bash "$render" "$tmp/one.md" >/dev/null
[ -s "$tmp/one.png" ] || { echo "FAIL: one.png missing"; exit 1; }

# several blocks: one PNG per block, numbered; the yaml block is ignored
bash "$render" "$tmp/two.md" >/dev/null
[ -s "$tmp/two-1.png" ] && [ -s "$tmp/two-2.png" ] || { echo "FAIL: two-1.png/two-2.png missing"; ls "$tmp"; exit 1; }
[ ! -e "$tmp/two-3.png" ] || { echo "FAIL: extra png"; exit 1; }

echo "PASS"
