"""Self-check for gate.check_commit. Run: python -I tests/test_gate_commitmsg.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
from gate_fixtures import make_repo, run, stage, write  # noqa: E402

CFG = {"test_commands": [], "sensitive": ["**/auth/**"], "architecture": gate.DEFAULT_ARCH}
BASE = {"README.md": "hi\n", "src/a.py": "a = 1\n", "src/b.py": "b = 1\n",
        "src/auth/x.py": "x = 1\n", "src/中 文.py": "z = 1\n"}


def change(tier="T2", status="partial"):
    return f"---\nstatus: {status}\ntier: {tier}\n---\n\n## Goal\nx\n"


def errs(repo, msg):
    return gate.check_commit(repo, msg, CFG)


def has(e, word):
    return any(word in x for x in e)


# message without Tier
r = make_repo(BASE)
stage(r, {"README.md": "2\n"})
assert has(errs(r, "msg\n"), "Tier")
assert errs(r, "msg\n\nTier: T0\n") == []
assert errs(r, "msg\r\n\r\nTier: T0\r\n") == []  # CRLF
assert has(errs(r, "msg\n# Tier: T0\n"), "Tier")  # comment lines dropped

# T0
r = make_repo(BASE)
stage(r, {"src/a.py": "a = 2\n"})
assert has(errs(r, "m\n\nTier: T0\n"), "T2")
r = make_repo(BASE)
stage(r, {".github/workflows/x.yml": "on: push\n"})
assert errs(r, "m\n\nTier: T0\n")
r = make_repo(BASE)
run(r, "mv", "src/a.py", "src/c.py")
assert errs(r, "m\n\nTier: T0\n") == []

# R100 rename of a high path is still high; plain source rename passes
r = make_repo({**BASE, ".github/workflows/a.yml": "on: push\n"})
run(r, "mv", ".github/workflows/a.yml", ".github/workflows/b.yml")
assert errs(r, "m\n\nTier: T0\n")
r = make_repo(BASE)
run(r, "mv", "src/a.py", "src/auth/a.py")
assert errs(r, "m\n\nTier: T0\n")  # into a sensitive dir
r = make_repo(BASE)
run(r, "mv", "src/a.py", "src/c.py")
assert errs(r, "m\n\nTier: T0\n") == []

# T1
r = make_repo(BASE)
stage(r, {"src/new.py": "n = 1\n"})
assert has(errs(r, "m\n\nTier: T1\n"), "T2")
r = make_repo(BASE)
stage(r, {"src/a.py": "a = 2\n", "tests/test_a.py": "pass\n"})
assert errs(r, "m\n\nTier: T1\n") == []
r = make_repo(BASE)
stage(r, {"src/a.py": "a = 2\n", "src/b.py": "b = 2\n"})
assert has(errs(r, "m\n\nTier: T1\n"), "T2")
r = make_repo(BASE)
stage(r, {"src/auth/x.py": "x = 2\n"})
assert errs(r, "m\n\nTier: T1\n")
r = make_repo(BASE)
stage(r, {"src/中 文.py": "z = 2\n"})
assert errs(r, "m\n\nTier: T1\n") == []

# T2 / Change trailer
r = make_repo({**BASE, "docs/changes/c.md": change()})
stage(r, {"src/a.py": "a = 2\n", "src/b.py": "b = 2\n"})
assert has(errs(r, "m\n\nTier: T2\n"), "Change")
assert errs(r, "m\n\nTier: T2\nChange: docs/changes/c.md\n") == []
assert errs(r, "m\n\nTier: T2\nChange: docs/changes/c.md\r\n") == []
assert errs(r, "m\n\nTier: T2\nChange: docs/changes/missing.md\n")
assert errs(r, "m\n\nTier: T3\nChange: docs/changes/c.md\n")  # tier mismatch
stage(r, {"docs/changes/c.md": change(status="shipped")})
assert errs(r, "m\n\nTier: T2\nChange: docs/changes/c.md\n")

# T1: one M source plus one pure R100 source rename passes
r = make_repo(BASE)
run(r, "mv", "src/b.py", "src/d.py")
stage(r, {"src/a.py": "a = 2\n"})
assert errs(r, "m\n\nTier: T1\n") == []

# T1 + Change pointing at a tier:T1 change must not skip the limits
r = make_repo({**BASE, "docs/changes/c1.md": change(tier="T1")})
stage(r, {"src/a.py": "a = 2\n", "src/b.py": "b = 2\n"})
e = errs(r, "m\n\nTier: T1\nChange: docs/changes/c1.md\n")
assert has(e, "T2 or T3") and has(e, "looks like T2")

# open change without Change trailer
r = make_repo({**BASE, "docs/changes/c.md": change()})
stage(r, {"src/a.py": "a = 2\n"})
assert gate.open_changes(r) == ["docs/changes/c.md"]
assert errs(r, "m\n\nTier: T1\n")
r = make_repo({**BASE, "docs/changes/c.md": change()})
stage(r, {"README.md": "2\n"})
assert errs(r, "m\n\nTier: T1\n") == []

# merge
r = make_repo(BASE)
stage(r, {"src/a.py": "a = 2\n", "src/b.py": "b = 2\n"})
write(r, {".git/MERGE_HEAD": run(r, "rev-parse", "HEAD")})
assert errs(r, "m\n\nTier: T1\n") == []
assert has(errs(r, "m\n"), "Tier")

# first commit, no HEAD
r = make_repo({}, commit=False)
stage(r, {"README.md": "hi\n"})
assert errs(r, "m\n\nTier: T0\n") == []
assert gate.staged(r) == [("A", "README.md")]

print("ok")
