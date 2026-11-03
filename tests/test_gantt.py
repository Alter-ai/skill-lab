"""Self-check for skills/backlog/scripts/gantt.py.

Run: uv run --with matplotlib python -I tests/test_gantt.py
"""
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "backlog" / "scripts"))
import gantt  # noqa: E402

SAMPLE = """# Backlog

## 時程

| 項目 | 開始 | 結束 | 里程碑 |
|---|---|---|---|
| 需求分析 | 2026-11-03 | 2026-11-16 | |
| 工作執行計畫書 | 2026-11-17 | 2026-11-17 | 是 |

## 完成標準
| 不是時程 | 2026-01-01 | 2026-01-02 | |
"""

rows = gantt.parse_schedule(SAMPLE)
assert rows == [
    ("需求分析", date(2026, 11, 3), date(2026, 11, 16), False),
    ("工作執行計畫書", date(2026, 11, 17), date(2026, 11, 17), True),
], rows

for bad, msg in [
    ("| a | 2026-13-01 | 2026-11-16 | |", "row 1"),
    ("| a | 2026-11-20 | 2026-11-16 | |", "ends before"),
]:
    try:
        gantt.parse_schedule("## 時程\n| 項目 | 開始 | 結束 | 里程碑 |\n|---|---|---|---|\n" + bad)
    except ValueError as e:
        assert msg in str(e), e
    else:
        raise AssertionError(f"expected ValueError for {bad}")

try:
    gantt.parse_schedule("# no schedule here")
except ValueError as e:
    assert "時程" in str(e), e
else:
    raise AssertionError("expected ValueError when the section is missing")

with tempfile.TemporaryDirectory() as t:
    out = Path(t) / "g.png"
    gantt.render(rows, out)
    assert out.stat().st_size > 1000, out.stat().st_size
print("ok")
