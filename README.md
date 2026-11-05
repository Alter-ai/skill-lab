# skill-lab

English | [繁體中文](README.zh-TW.md)

Personal [Claude Code](https://claude.com/claude-code) skills, plus the small tools used to build and check them: a commit gate that makes an AI session declare how risky its change is, a linter for `SKILL.md` files, and a routing test set.

## What problem it solves

An AI coding session tends to take the shortest path: skip the spec, skip the test, skip the review. Instructions in a prompt only make good behaviour more likely. This repo tries to make the key steps checkable:

- **Tier gate** (`tools/gate.py`): a `commit-msg` hook. When a Claude Code session commits, the message must carry `Tier: T0..T3`; T2/T3 changes must also point to a change file in `docs/changes/` that passes the rules in the `change-record` skill. Otherwise the commit is blocked.
- **Skill audit** (`tools/skill_audit.py`): static checks on `SKILL.md` files: size, frontmatter limits, dangling references, body overlap between skills.
- **Routing evals** (`evals/routing.json`): prompts with the expected skill or behaviour, and what was actually observed, so a change to a skill description can be compared with a baseline.

## Quick start (about 5 minutes)

Needs Python 3.13 and git.

```bash
git clone https://github.com/Alter-ai/skill-lab
cd skill-lab
python -I tests/test_skill_audit.py          # prints: ok
python -I tools/skill_audit.py local=skills  # lint the skills in this repo
```

Try the gate in a throwaway repo:

```bash
mkdir demo && cd demo && git init
echo 'test_commands = []' > .agent-gate     # this file turns the gate on for the repo
echo hi > a.txt && git add .
python ../skill-lab/tools/gate.py install   # installs .git/hooks/commit-msg
CLAUDE_CODE_CHILD_SESSION=1 git commit -m "x"
```

Expected:

```
gate: blocked (see skill change-record)
missing 'Tier: T0|T1|T2|T3' trailer in commit message
```

The hook only acts when `CLAUDE_CODE_CHILD_SESSION=1`, which Claude Code sets in its own sessions. A plain `git commit` in your terminal is not checked.

To use the skills, copy the directories you want from `skills/` into `~/.claude/skills/`. `examples/CLAUDE.md` is the user-level rule file (tier table and skill routing) the author runs with; adapt it before using it.

## What is in here

Written in this repo (MIT):

| Path | What |
|---|---|
| `skills/change-record` | change-file template and the gate's rules |
| `skills/backlog` | solo Scrum backlog, with a Gantt chart script |
| `skills/web-visual-design` | colour, Chinese/Latin type and layout guidance, with `palette_check.py` for WCAG contrast |
| `skills/oss-release-readiness` | pre-publication check of HEAD and all history, with `release_check.py` |
| `tools/` | `gate.py`, `skill_audit.py` |
| `tests/` | one self-checking script per file; each prints `ok` |
| `docs/` | architecture, change records, research notes |

Imported from other projects. Each directory keeps its own `LICENSE` and a `SOURCE.md` with the upstream commit:

| Skill | Upstream | License |
|---|---|---|
| api-and-interface-design, ci-cd-and-automation, documentation-and-adrs, frontend-ui-engineering, git-workflow-and-versioning, performance-optimization, security-and-hardening, shipping-and-launch | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT |
| c4-architecture | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) | MIT |
| frontend-design, webapp-testing | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 |
| competitive-brief, synthesize-research, user-research, ux-copy | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Apache-2.0 |

The root `LICENSE` covers only what the author wrote. The directories above follow their own licenses.

## How AI was used

Most of this repo was written by Claude Code under the author's direction, using the same workflow the repo describes. The author set the goals and the rules, read and decided on the designs, and runs the tools. Each change has a record in `docs/changes/` that says what was verified and by whom; the tests were written by the AI, and a separate AI reviewer checked each feature change. This is not independent human review of every line. Treat the code as you would any unaudited personal tool.

## Known limits

- Developed and tested on Windows 11 with Python 3.13. CI also runs on Ubuntu; Linux and macOS use is less tested.
- The gate only acts inside Claude Code sessions. It does not stop a human. `gate.py` also has `pretool` and `evidence` subcommands meant to run as Claude Code hooks (they block attempts to bypass the commit hook); the quick start does not set those up, and wiring them in `settings.json` is manual.
- `tests/test_render.sh` needs mermaid-cli and is not run in CI. `tests/test_gantt.py` needs `matplotlib`.
- Routing results come from small samples of headless runs, not a statistical study.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Contact: lericai0705@gmail.com.
