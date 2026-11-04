#!/usr/bin/env bash
# Render every ```mermaid block of a markdown file to PNG.
# One block -> <name>.png; several -> <name>-1.png, <name>-2.png, ... in file order.
# usage: bash scripts/render.sh docs/architecture/ARCHITECTURE.md [out.png]
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
awk -v dir="$tmp" '/^```mermaid/{n++; f=1; next} f && /^```/{f=0; next} f{print > (dir "/" n ".mmd")}' "$in"
count=$(ls "$tmp"/*.mmd 2>/dev/null | wc -l)
[ "$count" -gt 0 ] || { echo "no mermaid block in $in" >&2; exit 1; }
for i in $(seq 1 "$count"); do
  if [ "$count" -eq 1 ]; then o="$out"; else o="${out%.png}-$i.png"; fi
  "$mmdc" -q -i "$tmp/$i.mmd" -o "$o" -b white -s 2
  echo "wrote $o"
done
