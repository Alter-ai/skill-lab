"""Self-check for skills/oss-release-readiness/scripts/release_check.py. Run: python -I tests/test_release_check.py"""
import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "skills" / "oss-release-readiness" / "scripts"))
from gate_fixtures import make_repo, run, write  # noqa: E402
import release_check as rc  # noqa: E402

S = "secret@example.com"
BASE = {"LICENSE": "MIT\n", "README.md": "hi\n", "SECURITY.md": "report\n"}


def repo(extra=None, **kw):
    return make_repo({**BASE, **(extra or {})}, gate=None, **kw)


def first(out, prefix):
    return [f for f in out if f.startswith(prefix)]


def commit(r, msg="c"):
    run(r, "add", "-A")
    run(r, "commit", "-q", "-m", msg)


def quiet_main(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        return rc.main(argv), buf.getvalue()


assert rc.scan(repo(), [S]) == []

r = repo({"docs/a.txt": f"x\nMail {S.upper()} here\n", "中文/檔案.txt": f"{S}\n"})
out = rc.scan(r, [S])
assert "forbid[0] content docs/a.txt:2" in out, out
assert "forbid[0] content 中文/檔案.txt:1" in out, out

# added in commit 1, removed in commit 2: HEAD clean, history not
r = repo({"n.txt": f"{S}\n"})
write(r, {"n.txt": "clean\n"})
commit(r)
out = rc.scan(r, [S])
assert not first(out, "forbid[0] content"), out
assert "forbid[0] history 2 commits" in out, out

# author email, and a forbid value that starts with a dash
r = repo()
run(r, "commit", "-q", "--allow-empty", "-m", "e", f"--author=A <{S}>")
out = rc.scan(r, [S])
assert first(out, "forbid[0] author-email 1 commits"), out
assert rc.scan(repo({"d.txt": "a -x\\p b\n"}), ["-x\\p"]) == ["forbid[0] content d.txt:1", "forbid[0] history 1 commits"]

r = repo({"a/Zone.Identifier": "z", ".env": "k", "k.pem": "p", "x.key": "k", "ok.txt": "o"})
run(r, "rm", "-q", "-f", ".env", "k.pem")
run(r, "commit", "-q", "-m", "rm")
out = rc.scan(r, [])
assert sorted(first(out, "sensitive-path")) == sorted(
    f"sensitive-path {p}" for p in ["a/Zone.Identifier", ".env", "k.pem", "x.key"]), out

nb = lambda outs: json.dumps({"cells": [{"cell_type": "code", "outputs": outs}]})  # noqa: E731
out = rc.scan(repo({"dirty.ipynb": nb([{"output_type": "stream"}]), "clean.ipynb": nb([])}), [])
assert out == ["notebook-output dirty.ipynb"], out

r = repo()
(r / "big.bin").write_bytes(b"\0" * (5 * 1024 * 1024 + 1))
(r / "edge.bin").write_bytes(b"\0" * (5 * 1024 * 1024))
commit(r)
assert rc.scan(r, []) == ["large-file big.bin"]

out = rc.scan(make_repo({"README.md": "x\n"}, gate=None), [])
assert sorted(out) == ["missing LICENSE", "missing SECURITY.md"], out

sha = "a" * 40
out = rc.scan(repo({
    "skills/nosrc/LICENSE": "l", "skills/nosrc/SKILL.md": "s",
    "skills/badsha/LICENSE": "l", "skills/badsha/SOURCE.md": "Upstream: abc123\n",
    "skills/good/LICENSE": "l", "skills/good/SOURCE.md": f"Upstream: https://x/y @ {sha}\n",
    "skills/own/SKILL.md": "s"}), [])
assert sorted(out) == ["attribution skills/badsha", "attribution skills/nosrc"], out

# findings never echo the forbidden string
r = repo({f"{S}.txt": S, "x.txt": S})
run(r, "commit", "-q", "--allow-empty", "-m", "e", f"--author=A <{S}>")
out = rc.scan(r, [S])
assert out and not any(S in f for f in out), out

# main exit codes
import tempfile  # noqa: E402
with tempfile.TemporaryDirectory() as t:
    assert quiet_main([t])[0] == 2
r = make_repo({}, gate=None, commit=False)
assert quiet_main([str(r)])[0] == 2
r = repo()
run(r, "update-ref", "refs/remotes/origin/main", "HEAD")
run(r, "symbolic-ref", "HEAD", "refs/heads/unborn")
code, text = quiet_main([str(r)])
assert code == 2 and "no commits" in text, (code, text)
assert quiet_main([str(repo())]) == (0, "")
code, text = quiet_main([str(repo({"a.txt": S})), "--forbid", S])
assert code == 1 and "forbid[0] content a.txt:1" in text and S not in text, text
print("ok")
