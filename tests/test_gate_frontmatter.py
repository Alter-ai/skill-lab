"""Self-check for tools/gate.py parse_front_matter/section. Run: python -I tests/test_gate_frontmatter.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gate  # noqa: E402

DOC = """---
tier: T2                     # T2 | T3
status: partial              # proposed | partial | done | abandoned
components: [api, auth]      # ARCHITECTURE.md 的元件 id
evidence: [src/auth.py:42]   # path:line
verified_by:
  - pytest tests/test_auth.py          # 至少一條
  - "manual: localhost 登入成功"        # 機器無法驗證
reviewed_by: [fresh-context subagent]
supersedes: []
---
## 為什麼
因為。
## 行為改變
## 決策（含 Rulings）
## 沒做／已知限制
- 無
"""
for nl in ("\n", "\r\n"):
    fm, body = gate.parse_front_matter(DOC.replace("\n", nl))
    assert fm["tier"] == "T2" and fm["status"] == "partial", fm
    assert fm["components"] == ["api", "auth"], fm
    assert fm["evidence"] == ["src/auth.py:42"], fm
    assert fm["verified_by"] == ["pytest tests/test_auth.py", "manual: localhost 登入成功"], fm
    assert fm["reviewed_by"] == ["fresh-context subagent"], fm
    assert fm["supersedes"] == [], fm
    assert gate.section(body, "決策") == "", repr(gate.section(body, "決策"))
    assert gate.section(body, "為什麼") == "因為。"
    assert gate.section(body, "沒做") == "- 無"
    assert gate.section(body, "不存在") == ""

assert gate.parse_front_matter("# hi\n") == ({}, "# hi\n")
fm, _ = gate.parse_front_matter("---\na: 'x # y' # c\nb: v#w\nc:\n---\nbody")
assert fm == {"a": "x # y", "b": "v#w", "c": []}, fm
SKILL = (Path(__file__).resolve().parents[1] / "skills/change-record/SKILL.md").read_text(encoding="utf-8")
tpl = SKILL.split("```markdown\n---\n", 1)[1].split("\n---\n", 1)[0]
fm, _ = gate.parse_front_matter("---\n" + tpl + "\n---\n")
assert fm["evidence"] == ["src/auth.py:42"], fm
assert len(fm["verified_by"]) == 2, fm
print("ok")
