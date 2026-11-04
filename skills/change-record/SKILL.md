---
name: change-record
description: Use when writing or updating a docs/changes file, when a commit is blocked by the tier gate, or when setting up .agent-gate. Covers the change-file template, the commit-msg gate rules, Tier and Change trailers, and what to do when the gate blocks.
---

# Change Record

A change file is the handoff record for one change (not one commit): what changed, why, and how it was verified. It lives at `docs/changes/YYYY-MM-DD-<slug>.md`. The gate (`gate.py`, a git `commit-msg` hook) only runs in repos that have `.agent-gate`, and only for Claude sessions.

## Template

The four headings stay in Chinese; the gate and readers expect them.

```markdown
---
tier: T2                     # T2 | T3
status: partial              # proposed | partial | done | abandoned
components: [api, auth]      # component ids from ARCHITECTURE.md
evidence: [src/auth.py:42]   # path:line inside this change's diff
verified_by:
  - pytest tests/test_auth.py          # at least one must match test_commands
  - "manual: localhost 登入成功"        # machine cannot verify; highlighted
reviewed_by: [fresh-context subagent]
supersedes: []
---
## 為什麼
## 行為改變
## 決策（含 Rulings）
## 沒做／已知限制
```

## Fields

- `tier`: T2 or T3, equal to the commit's `Tier:` trailer. `status`: one of the four values above.
- `components`: ids that exist in the YAML of ARCHITECTURE.md.
- `evidence` and `verified_by`: write them as block lists (`- item` lines). The parser splits inline `[a, b]` lists on commas, so a command containing a comma breaks.
- `evidence`: each `path:line` must fall inside this change's diff and must not be a doc file.
- `verified_by`: `manual:` entries are allowed but never count as test evidence.
- `reviewed_by`: who reviewed; must be non-empty on `done`.
- A `done` change is history: do not edit it afterwards. When a superpowers SDD ledger is deleted at the end, copy its Rulings into `## 決策` first.

## .agent-gate

TOML at the repo root. Its presence turns the gate on.

```toml
test_commands = ["pytest", "uv run --isolated --no-project --python 3.13 pytest"]  # prefix match
sensitive     = ["**/auth/**", "**/payments/**", "migrations/**"]                  # touching = at least T2
architecture  = "docs/architecture/ARCHITECTURE.md"                                # default if omitted
```

## Gate rules (commit-msg)

1. File classes (matched by path segment, so `inspect.py` is not a test): docs (`*.md`, `*.txt`, `docs/`), low-risk config (other json/yaml/toml/ini), high-risk (`.github/`, CI files, dependency manifests and lockfiles, `.claude/`, `.agent-gate`, and `.agent-gate` `sensitive` globs), tests, source (everything else).
2. Every commit needs `Tier: T0`-`T3`. T0: docs, low-risk config or pure renames only. T1: at most one modified non-test source file, no new source files, no high-risk paths. Otherwise it is T2.
3. T2/T3 need `Change: docs/changes/<file>.md`, and the file must exist in the index. The change file `tier` must be T2 or T3 and equal the commit's Tier. Every commit that belongs to a T2/T3 change carries that change's Tier and Change trailers. While any change is `proposed` or `partial`, every commit touching source or test files must carry `Change:`, whatever its Tier.
4. Every commit: front matter `tier` matches the trailer and `status` is valid.
5. Full verification runs only on the commit that sets `status: done`. "This change" means the cumulative diff from the parent of the commit where the change file first appeared up to the index.
   - Every component exists in ARCHITECTURE.md's YAML.
   - If `## 行為改變` is non-empty, ARCHITECTURE.md must have changed within the change. To skip this, state in the change file that there is no behavior change.
   - Every `evidence` `path:line` points into this change's diff and is not a doc file.
   - `verified_by` has at least one entry matching `test_commands`, and the last successful recorded test run tested exactly the code being committed. Re-run the tests after the final code edit, from the repo's own directory as the session working directory.
   - `reviewed_by` is non-empty and a subagent was dispatched whose prompt contains the change file's path.
   - T3 also needs a non-empty `## 決策` section.
6. Merge commits: only the `Tier:` trailer is checked.

Trailer format (also in git-workflow-and-versioning):

```
Tier: T2
Change: docs/changes/2026-11-04-login.md
```

## Reviewer evidence

Give the fresh-context reviewer only the diff and the requirement, with the change file's path in the prompt. Every conclusion it returns must cite `path:line` or a command that was actually run. Drop conclusions without either.

## When the gate blocks

The first stderr line is `gate: blocked (see skill change-record)`, followed by one reason per line. Fix only what the reasons list (add the trailer, fill the field, re-run the tests) or stop and ask the user. Never work around it:

- no `--no-verify`, no `core.hooksPath`, no changing `CLAUDE_CODE_CHILD_SESSION`;
- do not lower the Tier or edit gate files (`.agent-gate`, hooks, evidence log);
- the PreToolUse hook also blocks `git cherry-pick`, `revert`, `rebase`, `am`, `commit-tree` and `update-ref`; ask the user to run those.

The user's own terminal commit is the only legitimate bypass.

## 待人工確認

At the end of a T2/T3 reply (and the first paragraph of a PR description), list what the machine could not verify. Highlight only: every `manual:` item, `reviewed_by`, and any retro warning from the PreToolUse hook (earlier commits missing `Tier:`).

```
待人工確認
- manual: localhost 登入成功
- reviewed_by: fresh-context subagent（只證明有派發，不證明審得好）
- 警告: abc1234 缺少 Tier trailer
```
