#!/usr/bin/env bash
# Render the first ```mermaid block of a markdown file to PNG.
# usage: bash scripts/render.sh docs/architecture/c4-context.md [out.png]
set -euo pipefail
in="$1"
out="${2:-${in%.md}.png}"
mmdc="${MMDC:-$HOME/.local/mermaid-cli/node_modules/.bin/mmdc}"
[ -x "$mmdc" ] || {
  echo "mmdc not found at $mmdc. Install: npm install --prefix ~/.local/mermaid-cli @mermaid-js/mermaid-cli@11.17.0" >&2
  exit 1
}
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
awk '/^```mermaid/{f=1; next} f && /^```/{exit} f' "$in" > "$tmp/d.mmd"
[ -s "$tmp/d.mmd" ] || { echo "no mermaid block in $in" >&2; exit 1; }
"$mmdc" -q -i "$tmp/d.mmd" -o "$out" -b white -s 2
echo "wrote $out"
