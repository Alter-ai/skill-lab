# skill-lab

English | [繁體中文](README.zh-TW.md)

Personal [Claude Code](https://claude.com/claude-code) skills, plus the small tools used to build and check them: a commit gate that makes an AI session declare how risky its change is, a linter for `SKILL.md` files, and a routing test set.

## What problem it solves

An AI coding session tends to take the shortest path: skip the spec, skip the test, skip the review. Instructions in a prompt only make good behaviour more likely. This repo tries to make the key steps checkable:

- **Tier gate** (`tools/gate.py`): a `commit-msg` hook. When a Claude Code session commits, the message must carry `Tier: T0..T3`; T2/T3 changes must also point to a change file in `docs/changes/` that passes the rules in the `change-record` skill. Otherwise the commit is blocked.
- **Skill audit** (`tools/skill_audit.py`): static checks on `SKILL.md` files: size, frontmatter limits, dangling references, body overlap between skills.
- **Routing evals** (`evals/routing.json`): prompts with the expected skill or behaviour, and what was actually observed, so a change to a skill description can be compared with a baseline.

## Quick start (about 5 minutes)

Needs Python 3.13 and git. Use `python3` instead of `python` where that is the name on Linux or macOS.

```bash
git clone https://github.com/Alter-ai/skill-lab
cd skill-lab
python -I tests/test_skill_audit.py          # prints: ok
python -I tools/skill_audit.py local=skills  # lint the skills in this repo
```

Try the gate in a throwaway repo (the quick start is bash syntax; on Windows use Git Bash):

```bash
cd ..                                        # leave skill-lab; the demo repo is a sibling
mkdir demo && cd demo && git init
git config user.name you && git config user.email you@example.com   # git needs an identity to commit
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

The hook only acts when `CLAUDE_CODE_CHILD_SESSION=1`. In the author's test (Claude Code desktop on Windows 11, see `docs/changes/2026-11-04-hook-payload-spike.md`) the Bash and PowerShell tools had it set; other versions and platforms are not verified. A plain `git commit` in your terminal is not checked.

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
| `evals/` | routing cases and eval results |
| `examples/CLAUDE.md` | the user-level rule file (tier table, skill routing) |
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

Most of this repo was written by Claude Code under the author's direction, using the workflow the repo describes. The author set the goals and the rules, read and decided on the designs, and runs the tools. The tests were also written by the AI. Since the gate was enabled, T2 and T3 changes have a change file in `docs/changes/` and most had a fresh-context AI review; earlier commits did not, and not every commit carries a `Tier:` trailer. There was no independent human review of every line. Treat the code as you would any unaudited personal tool.

## Known limits

- Developed and tested on Windows 11 with Python 3.13. CI is configured to run on Ubuntu as well, but that has not been confirmed yet; Linux and macOS use is less tested.
- The gate only acts inside Claude Code sessions. It does not stop a human. `gate.py` also has `pretool` and `evidence` subcommands meant to run as Claude Code hooks (they block attempts to bypass the commit hook); the quick start does not set those up, and wiring them in `settings.json` is manual.
- `tests/test_render.sh` needs mermaid-cli and is not run in CI. `tests/test_gantt.py` needs `matplotlib`.
- The `web-visual-design` skill was evaluated on 3 briefs by AI reviewers, nothing was rendered, and no human saw the results; see [evals/results/2026-11-web-visual-design.md](evals/results/2026-11-web-visual-design.md).
- Routing results come from small samples of headless runs, not a statistical study.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Contact: lericai0705@gmail.com.
