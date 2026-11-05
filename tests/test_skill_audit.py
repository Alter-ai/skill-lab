"""Self-check for tools/skill_audit.py. Run: python -I tests/test_skill_audit.py"""
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import skill_audit as sa  # noqa: E402


def mk(root, name, body, fm_name=None, desc="Does a thing. Use when testing."):
    d = root / name
    d.mkdir()
    (d / "SKILL.md").write_text(f"---\nname: {fm_name or name}\ndescription: {desc}\n---\n{body}", encoding="utf-8")


with tempfile.TemporaryDirectory() as t:
    r = Path(t)
    mk(r, "ok", "a perfectly fine line that is long enough\n")
    mk(r, "big", "x\n" * 600)
    mk(r, "bad", "see t:nope and foo-bar:baz-qux and path:line and w:author and `scripts/none.py` and [a](gone.md)\n",
       fm_name="Bad_Name", desc="d" * 1100)
    shared = "\n".join(f"this is shared line number {i} in both" for i in range(10))
    mk(r, "dup1", shared)
    mk(r, "dup2", shared + "\nplus one extra line only in dup2 here")

    skills = sa.load_all({"t": r})
    known = set(skills)
    fl = {k: sa.flags(s, known) for k, s in skills.items()}

    assert fl["t:ok"] == [], fl["t:ok"]
    assert fl["t:big"] == ["lines>500"], fl["t:big"]
    assert fl["t:bad"] == sorted(["bad-name", "name!=dir", "desc>1024", "ref?t:nope", "ref?foo-bar:baz-qux",
                                  "missing-file:scripts/none.py", "missing-file:gone.md"]), fl["t:bad"]
    top = sa.overlap(skills, 90)
    assert len(top) == 1 and {top[0][3], top[0][4]} == {"t:dup1", "t:dup2"}, top

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = sa.main([f"t={r}", "--overlap", "90", "--json"])
    out = json.loads(buf.getvalue())
    assert code == 1 and out["flagged"] == 2, (code, out["flagged"])  # t:big and t:bad
    rows = {row["skill"]: row for row in out["skills"]}
    assert rows["t:big"]["flags"] == ["lines>500"] and rows["t:ok"]["flags"] == [], rows
    assert rows["t:big"]["lines"] > 500, rows["t:big"]
    assert [{o["a"], o["b"]} for o in out["overlap"]] == [{"t:dup1", "t:dup2"}], out["overlap"]
src = Path(sa.__file__).read_text(encoding="utf-8")
assert "Users\\" not in src and "claude_pzs" not in src, "machine-specific path in skill_audit.py"
print("ok")
