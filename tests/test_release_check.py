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
# --- fix round 1 ---
import os  # noqa: E402
import stat  # noqa: E402

# commit messages and tags (message, tagger email) are scanned; findings stay quiet
r = repo()
run(r, "commit", "-q", "--allow-empty", "-m", f"note {S}")
out = rc.scan(r, [S])
assert "forbid[0] commit-message 1 commits" in out and not any(S in f for f in out), out
r = repo()
run(r, "tag", "-a", "v1", "-m", f"tag {S}")
assert "forbid[0] tag 1 tags" in rc.scan(r, [S])
r = repo()
run(r, "-c", f"user.email={S}", "tag", "-a", "v2", "-m", "x")
out = rc.scan(r, [S])
assert "forbid[0] tag 1 tags" in out and not first(out, "forbid[0] author-email"), out

# only the file name carries the string
out = rc.scan(repo({f"{S}-notes.txt": "clean"}), [S])
assert out == ["forbid[0] path-head 1 files", "forbid[0] path-history 1 files"], out
r = repo({f"{S}-old.txt": "clean"})
run(r, "rm", "-q", f"{S}-old.txt")
commit(r)
out = rc.scan(r, [S])
assert not first(out, "forbid[0] path-head") and "forbid[0] path-history 1 files" in out, out

# submodule (gitlink) has size "-"
r = repo()
run(r, "update-index", "--add", "--cacheinfo", f"160000,{'b' * 40},sub")
run(r, "commit", "-q", "-m", "sub")
assert rc.scan(r, []) == []

# notebooks: v3 outputs, unreadable
out = rc.scan(repo({"v3.ipynb": json.dumps({"worksheets": [{"cells": [{"outputs": [{"o": 1}]}]}]}),
                    "bad.ipynb": "not json"}), [])
assert out == ["notebook-unreadable bad.ipynb", "notebook-output v3.ipynb"] or \
    sorted(out) == ["notebook-output v3.ipynb", "notebook-unreadable bad.ipynb"], out

# forbid validation
for bad in ("--forbid=", "--forbid=a\nb"):
    assert quiet_main([str(repo()), bad])[0] == 2, bad

# sensitive paths: case-insensitive, .env.*
out = rc.scan(repo({"KEY.PEM": "p", ".env.local": "k", "env.txt": "e"}), [])
assert sorted(out) == ["sensitive-path .env.local", "sensitive-path KEY.PEM"], out

# run from a subdirectory
r = repo({"sub/x.txt": "ok", "top.txt": S})
code, text = quiet_main([str(r / "sub"), f"--forbid={S}"])
assert code == 1 and "forbid[0] content top.txt:1" in text, (code, text)

# binary-only match at HEAD and in history
r = repo()
(r / "bin.dat").write_bytes(b"\0\0" + S.encode() + b"\0")
commit(r)
out = rc.scan(r, [S])
assert "forbid[0] content bin.dat binary" in out and "forbid[0] history 1 commits" in out, out

# all forbidden values are redacted in one pass, longest first
out = rc.scan(repo({"abc.txt": "abc\n"}), ["ab", "abc"])
assert "forbid[0] content <forbid[1]>.txt:1" in out and "forbid[1] content <forbid[1]>.txt:1" in out, out

# author and committer names, ref names
r = repo()
run(r, "commit", "-q", "--allow-empty", "-m", "e", "--author=Jane Doe <a@example.com>")
out = rc.scan(r, ["jane doe"])
assert first(out, "forbid[0] author-email 1 commits") and not any("jane" in f.lower() for f in out), out
r = repo()
run(r, "-c", "user.name=Jane Doe", "commit", "-q", "--allow-empty", "-m", "e")
assert first(rc.scan(r, ["Jane Doe"]), "forbid[0] author-email 1 commits")
r = repo()
run(r, "tag", "projx-v1")
out = rc.scan(r, ["projx"])
assert out == ["forbid[0] ref 1 refs"], out
r = repo()
run(r, "branch", "projx-work")
assert rc.scan(r, ["projx"]) == ["forbid[0] ref 1 refs"]
assert rc.scan(repo(), ["projx"]) == []

# .env templates are not secrets
out = rc.scan(repo({".env.example": "k", ".env.sample": "k", "a/.env.template": "k", ".env.prod": "k"}), [])
assert out == ["sensitive-path .env.prod"], out

# non-ASCII file name with a legacy console encoding: backslash-escaped, not a traceback
import subprocess  # noqa: E402
r = repo({"é.pem": "p"})
p = subprocess.run([sys.executable, str(ROOT / "skills" / "oss-release-readiness" / "scripts" / "release_check.py"), str(r)],
                   capture_output=True, env={**os.environ, "PYTHONIOENCODING": "cp950"})
assert p.returncode == 1 and b"sensitive-path" in p.stdout and not p.stderr, (p.returncode, p.stdout, p.stderr)

# shallow clone sees partial history
r = repo()
run(r, "commit", "-q", "--allow-empty", "-m", "two")
import tempfile  # noqa: E402,F811
with tempfile.TemporaryDirectory() as t:
    run(r, "clone", "-q", "--depth=1", r.as_uri(), str(Path(t) / "c"))
    assert "shallow-clone" in rc.scan(Path(t) / "c", [])
assert "shallow-clone" not in rc.scan(r, [])

# case folding in redaction must not raise
out = rc.scan(repo({"ſecret.txt": "secret"}), ["secret"])
assert "forbid[0] content <forbid[0]>.txt:1" in out, out

# git failure is exit 2, not findings
r = repo()
tree = run(r, "rev-parse", "HEAD^{tree}").strip()
obj = r / ".git" / "objects" / tree[:2] / tree[2:]
os.chmod(obj, stat.S_IWRITE)
obj.unlink()
code, text = quiet_main([str(r)])
assert code == 2 and "git" in text, (code, text)
print("ok")
