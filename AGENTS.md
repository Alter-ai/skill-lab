# skill-lab

Personal Claude Code skills. Source of truth is `skills/`; deployed copies live in `~/.claude/skills/` (edit here, then copy).

- Tests: run each file on its own, e.g. `C:/Python313/python.exe -I tests/test_gate_cli.py` (prints `ok`). Skill lint: `C:/Python313/python.exe -I tools/skill_audit.py local=skills`.
- Commits are checked by the tier gate (`.agent-gate`, `tools/gate.py`): every commit needs a `Tier: T0`–`T3` trailer; T2/T3 changes need a change file in `docs/changes/`. Format and rules: skill `change-record` (`skills/change-record/SKILL.md`).
- Architecture: `docs/architecture/ARCHITECTURE.md`. Decisions: `docs/changes/`.
