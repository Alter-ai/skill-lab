# Contributing

Small project, one maintainer. Issues and pull requests are welcome; expect slow replies.

## Run the tests

Run each file on its own from the repo root. Each prints `ok` when it passes.

```bash
python -I tests/test_gate_cli.py
python -I tests/test_skill_audit.py
# ...one command per tests/test_*.py
python -I tools/skill_audit.py local=skills
```

`tests/test_gantt.py` needs `matplotlib`. `tests/test_render.sh` needs mermaid-cli and is not run in CI.

Developed and tested on Windows 11 with Python 3.13. CI also runs on Ubuntu.

## Tier rules

Every commit declares a risk tier in its message, and the tier gate (`tools/gate.py`) checks it when a Claude Code session commits. Humans are not blocked, but PRs should follow the same rules.

| Tier | When | Needs |
|---|---|---|
| T0 | docs or low-risk config only, or a pure rename | nothing extra |
| T1 | at most one existing non-test source file, no new source file, no behaviour change | a failing test first for a bug fix |
| T2 | new behaviour, several files, or high-risk paths such as `.github/` | a change file in `docs/changes/` and an independent review |
| T3 | new subsystem, public interface change, restructure | spec and plan in `docs/changes/`, review per task |

Commit trailers (the gate matches each as a whole line anywhere in the message by regex; they need not be in the final trailer block):

```
Tier: T2
Change: docs/changes/<date>-<topic>.md
```

The change-file format is in `skills/change-record/SKILL.md`.

## Third-party skills

Do not edit a skill that has a `SOURCE.md`; update it from upstream and record the new commit there.
