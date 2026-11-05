---
name: backlog
description: Keeps a solo developer's Scrum backlog in BACKLOG.md - product goal, user stories with acceptance criteria, MoSCoW priority, WBS, weekly schedule with a Gantt chart, Definition of Done, and sprint goal, review and retrospective. Use when starting a project, planning or closing a sprint, writing user stories or a WBS, picking the next item to build, or producing a schedule or Gantt chart for a report.
---

# Backlog (solo Scrum)

One file, `BACKLOG.md` at the repo root, is the product backlog, sprint board and schedule. Start it from [assets/BACKLOG.template.md](assets/BACKLOG.template.md).

## Solo adaptation of Scrum

Keep: a Product Goal, an ordered backlog, fixed-length sprints (1-2 weeks), a Sprint Goal, a Definition of Done, and a review plus retrospective at each sprint end.
Drop: daily stand-ups, story points, burndown charts, role ceremonies. One person holds Product Owner, Scrum Master and Developer at once.
Limit work in progress to 2 items. Finishing beats starting.

## Workflows

### New project
1. Copy the template to `BACKLOG.md`. Fill Product Goal and the first stories from the user's brief.
2. If the problem or users are unclear, use `user-research` and `competitive-brief` first; record findings as evidence under the story they support.
3. Draft the WBS and the 時程 table. Generate the chart (below). Ask the user to confirm priorities before any build work.

### Writing a story
- Format: `身為<角色>，我希望<能力>，以便<價值>`.
- Check INVEST: independent, negotiable, valuable, estimable, small (fits one sprint), testable.
- Acceptance criteria as `Given / When / Then`, each one checkable by a test or a demo step.
- Priority: Must / Should / Could / Won't (this release). The MVP is the Must set only.

### Sprint start
1. Write the Sprint Goal as one sentence of user-visible outcome.
2. Pull the top Must items that fit; move them to `進行中`.
3. Hand each item to `superpowers:brainstorming` (CLAUDE.md rule 1), then `superpowers:writing-plans`. The story's acceptance criteria become the plan's tests.

### Sprint end
1. Review: for each item, Done only if every Definition of Done line holds. Otherwise it returns to the backlog with what is left.
2. Retrospective: three lines - kept, change, try. A correction the user made twice becomes a proposed Gotcha; ask the user before adding it to CLAUDE.md or a skill.
3. Update 時程 if dates moved, and regenerate the chart.

### Gantt chart
Run from the skill directory against the project's file:

```bash
uv run --isolated --no-project --python 3.13 --with matplotlib python scripts/gantt.py <repo>/BACKLOG.md <repo>/docs/gantt.png
```

The script reads only the `## 時程` table (columns 項目 | 開始 | 結束 | 里程碑, dates `YYYY-MM-DD`; any text in 里程碑 draws a diamond). It stops with the row number on a bad date or an end before the start: fix the table, never hand-draw the chart.

## Gotchas

- `uv run` without `--isolated --no-project` picks up a parent `.venv`, and that environment may have a different Python or broken packages.
- matplotlib needs a CJK font for Chinese labels; the script asks for Microsoft JhengHei first.
- A course or client template may fix the report sections; keep BACKLOG.md as the source and copy from it into the report, not the reverse.
