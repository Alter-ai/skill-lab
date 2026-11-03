"""Draw a weekly Gantt chart (PNG) from the 時程 table in BACKLOG.md.

usage: uv run --with matplotlib python scripts/gantt.py BACKLOG.md gantt.png
Table columns: 項目 | 開始 | 結束 | 里程碑 (dates YYYY-MM-DD; any text in 里程碑 marks a milestone).
"""
import re
import sys
from datetime import date, timedelta
from pathlib import Path

HEADINGS = ("時程", "Schedule")
# Windows ships JhengHei; without a CJK font matplotlib draws empty boxes for Chinese labels
CJK_FONTS = ["Microsoft JhengHei", "Noto Sans CJK TC", "PingFang TC", "DejaVu Sans"]


def parse_schedule(text):
    m = re.search(rf"^##\s*({'|'.join(HEADINGS)})\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        raise ValueError("no '## 時程' (or '## Schedule') section found")
    rows = []
    for line in m.group(2).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not re.match(r"\d{4}-", cells[1]):
            continue  # header, separator or prose
        n = len(rows) + 1
        try:
            start, end = date.fromisoformat(cells[1]), date.fromisoformat(cells[2])
        except ValueError as e:
            raise ValueError(f"row {n} ({cells[0]}): {e}") from None
        if end < start:
            raise ValueError(f"row {n} ({cells[0]}) ends before it starts")
        rows.append((cells[0], start, end, len(cells) > 3 and bool(cells[3])))
    if not rows:
        raise ValueError("the 時程 table has no dated rows")
    return rows


def render(rows, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = CJK_FONTS
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(10, 0.45 * len(rows) + 1.5))
    for i, (name, start, end, milestone) in enumerate(rows):
        if milestone:
            ax.plot(start, i, marker="D", markersize=9, color="#c0392b")
        else:
            # +1 day so a task ending on a date covers that whole day
            ax.barh(i, (end - start + timedelta(days=1)).days, left=start, height=0.5, color="#2e86c1")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_ylim(len(rows) - 0.4, -0.6)  # first row on top; half a row of room keeps edge diamonds whole
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.grid(axis="x", color="#dddddd")
    ax.set_axisbelow(True)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    render(parse_schedule(Path(sys.argv[1]).read_text(encoding="utf-8")), sys.argv[2])
    print(f"wrote {sys.argv[2]}")
