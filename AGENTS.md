# skill-lab

Personal Claude Code skills. Source of truth is `skills/`; deployed copies live in `~/.claude/skills/` (edit here, then copy).

- Tests: run each file on its own, e.g. `C:/Python313/python.exe -I tests/test_gate_cli.py` (prints `ok`). Skill lint: `C:/Python313/python.exe -I tools/skill_audit.py local=skills`. `tests/test_gantt.py` needs matplotlib (`uv run --isolated --no-project --python 3.13 --with matplotlib python -I tests/test_gantt.py`); `tests/test_render.sh` needs mermaid-cli and is not in CI (`.github/workflows/test.yml`).
- Commits are checked by the tier gate (`.agent-gate`, `tools/gate.py`): every commit needs a `Tier: T0`–`T3` trailer; T2/T3 changes need a change file in `docs/changes/`. Format and rules: skill `change-record` (`skills/change-record/SKILL.md`).
- Architecture: `docs/architecture/ARCHITECTURE.md`. Decisions: `docs/changes/`.
- Public repo: `README.md` / `README.zh-TW.md`, `LICENSE` (MIT; `skills/` third-party dirs keep their own), `examples/CLAUDE.md` is the user-level rule file. Before any publish run `skills/oss-release-readiness/scripts/release_check.py`.
