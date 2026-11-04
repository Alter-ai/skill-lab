"""Self-check for gate.verify_done. Run: python -I tests/test_gate_done.py"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
from gate_fixtures import make_repo, run, stage  # noqa: E402

ARCH = "# A\n## AI structured data\n```yaml\ncomponents:\n  - id: api  # the api\n  - id: \"db\"\n```\n## Other\n- id: zzz\n"
ARCH_PATH = "docs/architecture/ARCHITECTURE.md"
CH = "docs/changes/2026-11-04-x.md"
A0 = "a=1\nb=2\nc=3\n"
A1 = "a=1\nb=9\nc=3\n"


def change(status="done", components="[api]", evidence="[src/a.py:2]", verified="[python -I tests x]",
           reviewed="[agent]", tier="T2", behavior="", decision="why"):
    return (f"---\nstatus: {status}\ntier: {tier}\ncomponents: {components}\nevidence: {evidence}\n"
            f"verified_by: {verified}\nreviewed_by: {reviewed}\n---\n## 行為改變\n{behavior}\n\n## 決策\n{decision}\n")


def build(log_test=True, log_agent=True, tier="T2", edit_after=False, fail_after=False, touch_arch=False,
          arch=True, **kw):
    files = {"src/a.py": A0, "README.md": "r"}
    if arch:
        files[ARCH_PATH] = ARCH
    repo = make_repo(files)
    stage(repo, {CH: change("partial", tier=tier)})
    run(repo, "commit", "-q", "-m", "add change")
    stage(repo, {"src/a.py": A1})
    if touch_arch:
        stage(repo, {ARCH_PATH: ARCH + "\nmore\n"})
    if log_test:
        gate.append_log(repo, {"t": time.time(), "kind": "test", "ok": True, "cmd": "python -I tests x",
                               "tree": gate.tree_snapshot(repo)})
    if edit_after:
        stage(repo, {"src/a.py": A1 + "d=4\n"})
    if fail_after:
        gate.append_log(repo, {"t": time.time(), "kind": "test", "ok": False, "cmd": "python -I tests x",
                               "tree": gate.tree_snapshot(repo)})
    if log_agent:
        gate.append_log(repo, {"t": time.time() + 10, "kind": "agent", "agent_type": "r", "prompt_paths": [CH]})
    stage(repo, {CH: change(tier=tier, **kw)})
    return repo


def errs(repo, tier="T2"):
    fm, body = gate.parse_front_matter(gate.index_text(repo, CH))
    return gate.verify_done(repo, CH, fm, body, gate.load_config(repo), tier, time.time())


def has(es, word):
    return any(word in e for e in es)


assert gate.architecture_ids(ARCH) == {"api", "db"}
assert errs(build()) == [], errs(build())
assert has(errs(build(components="[nope]")), "components")
assert has(errs(build(components="[]")), "components")
assert has(errs(build(behavior="changed")), "ARCHITECTURE")
assert errs(build(behavior="changed", touch_arch=True)) == []
assert errs(build(behavior="")) == []
assert has(errs(build(arch=False)), "ARCHITECTURE")
assert has(errs(build(evidence="[src/a.py:999]")), "evidence")
assert has(errs(build(evidence="[src/a.py:1]")), "evidence")  # line outside the hunk
e = errs(build(evidence="[src/a.py:999, src/a.py:998, src/a.py:2]"))
assert len([x for x in e if "evidence" in x]) == 2, e
assert has(errs(build(verified="[pytest]")), "verified_by")
assert has(errs(build(verified="[manual: looked]")), "verified_by")
assert errs(build(verified="[manual: looked, python -I tests x]")) == []
assert has(errs(build(log_test=False)), "verified_by")
e = errs(build(edit_after=True))
assert has(e, "src/a.py"), e
assert errs(build(fail_after=True)) == []  # Review Focus 5: later failures are ignored
assert has(errs(build(log_agent=False)), "reviewed_by")
assert has(errs(build(reviewed="[]")), "reviewed_by")
assert has(errs(build(tier="T3", decision=""), "T3"), "決策")
assert errs(build(tier="T3"), "T3") == []

# fix round 1
repo = build(log_test=False)
for rec in ({"tree": ""}, {}):
    gate.append_log(repo, {"t": time.time(), "kind": "test", "ok": True, "cmd": "python -I tests x", **rec})
assert has(errs(repo), "verified_by"), errs(repo)
assert has(errs(build(evidence=f"[{CH}:3]")), "evidence")
assert has(errs(build(evidence=f"[{ARCH_PATH}:1]", touch_arch=True)), "evidence")
repo = build()
run(repo, "mv", "src/a.py", "src/b.py")
assert any(e.startswith("verified_by: src/a.py changed") for e in errs(repo)), errs(repo)
repo = build()
stage(repo, {"src/c.py": "x = 1" + chr(10) + "++ b/other.py" + chr(10)})
hk = gate.hunks(repo, gate.change_base(repo, CH))
assert "other.py" not in hk and hk["src/c.py"] == [(1, 2)], hk

# base / hunks
repo = build()
base = gate.change_base(repo, CH)
assert base == gate.git(repo, "rev-parse", "HEAD~1").strip(), base
assert gate.hunks(repo, base)["src/a.py"] == [(2, 2)]
r2 = make_repo({"a": "1"}, commit=False)
assert gate.change_base(r2, CH) == gate.EMPTY_TREE
r3 = make_repo({"a": "1"})
assert gate.change_base(r3, CH) == "HEAD"
stage(r3, {CH: change("partial")})
run(r3, "commit", "-q", "-m", "c")
assert gate.change_base(r3, CH) == gate.git(r3, "rev-parse", "HEAD~1").strip()

# wiring: partial -> done through check_commit
repo = build()
msg = f"x\n\nTier: T2\nChange: {CH}\n"
assert gate.check_commit(repo, msg, gate.load_config(repo)) == []
repo = build(components="[nope]")
assert has(gate.check_commit(repo, msg, gate.load_config(repo)), "components")
print("ok")
