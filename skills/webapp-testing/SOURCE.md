# Source

- Upstream: https://github.com/anthropics/skills/tree/ca45fc496a3436251f191354091d557da31c15b5/skills/webapp-testing
- License: Apache-2.0 (see LICENSE)
- Copied: 2026-11-05; includes `scripts/` and `examples/` unchanged

## Local modifications

- `LICENSE.txt` -> `LICENSE`; frontmatter `license: Complete terms in LICENSE.txt` -> `license: Complete terms in LICENSE`.
- `examples/` and the SKILL.md snippet write to `/mnt/user-data/outputs/` (upstream sandbox path) and `/tmp/`; neither is valid on Windows, so change the paths before running them on this machine.
