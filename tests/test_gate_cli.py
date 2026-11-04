"""Self-check for tools/gate.py install + CLI. Run: python -I tests/test_gate_cli.py"""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
from gate_fixtures import make_repo, run, write  # noqa: E402

GATE = str(Path(gate.__file__).resolve()).replace("\\", "/")
HDR = "gate: blocked (see skill change-record)"


def hook(repo):
    return repo / ".git" / "hooks" / "commit-msg"


def commit(repo, msg, child, *extra):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_CHILD_SESSION"}
    if child:
        env["CLAUDE_CODE_CHILD_SESSION"] = "1"
    return subprocess.run(["git", "commit", "-q", *extra, "-m", msg], cwd=repo, env=env,
                          capture_output=True, text=True, encoding="utf-8")


# install writes an absolute-path hook, LF endings, executable
repo = make_repo({"src/a.py": "x = 1\n"})
msg = gate.install(repo, GATE)
assert isinstance(msg, str) and "\n" not in msg
raw = hook(repo).read_bytes()
text = raw.decode()
assert b"\r" not in raw and text.startswith("#!/bin/sh\n# installed by gate.py\n")
assert GATE in text and sys.executable.replace("\\", "/") in text and 'commit-msg "$1"' in text
if os.name == "posix":
    assert os.access(hook(repo), os.X_OK)

# re-install: idempotent, never makes .local from our own hook
gate.install(repo, GATE)
assert hook(repo).read_text() == text and not (hook(repo).parent / "commit-msg.local").exists()

# existing foreign hook -> .local, chained; failing old hook fails the commit
for code, ok in ((1, False), (0, True)):
    r = make_repo({"src/a.py": "x = 1\n"})
    hook(r).write_bytes(f"#!/bin/sh\nexit {code}\n".encode())
    gate.install(r, GATE)
    assert (hook(r).parent / "commit-msg.local").read_bytes() == f"#!/bin/sh\nexit {code}\n".encode()
    gate.install(r, GATE)  # must not clobber .local
    assert (hook(r).parent / "commit-msg.local").exists()
    write(r, {"src/a.py": "x = 2\n"})
    run(r, "add", "-A")
    p = commit(r, "plain", child=False)
    assert (p.returncode == 0) == ok, p.stderr

# local core.hooksPath refused
r = make_repo({"a.txt": "a\n"})
run(r, "config", "core.hooksPath", "somewhere")
try:
    gate.install(r, GATE)
    raise SystemExit("expected refusal")
except RuntimeError as e:
    assert "hooksPath" in str(e)
assert not hook(r).exists()

# e2e
repo = make_repo({"src/a.py": "x = 1\n"})
gate.install(repo, GATE)
write(repo, {"src/a.py": "x = 2\n"})
run(repo, "add", "-A")
p = commit(repo, "no trailer", child=True)
assert p.returncode != 0 and p.stderr.splitlines()[0] == HDR, p.stderr
assert any(x.get("kind") == "gate" and x.get("decision") == "block" for x in gate.read_log(repo))
p = commit(repo, "no trailer", child=False)
assert p.returncode == 0, p.stderr
write(repo, {"src/a.py": "x = 3\n"})
p = commit(repo, "tweak\n\nTier: T1", True, "-a")
assert p.returncode == 0, p.stderr
assert any(x.get("decision") == "allow" for x in gate.read_log(repo))

# malformed .agent-gate fails closed for child, ignored for humans
write(repo, {".agent-gate": "test_commands = [\n", "src/a.py": "x = 4\n"})
run(repo, "add", "-A")
p = commit(repo, "x\n\nTier: T1", child=True)
assert p.returncode != 0 and p.stderr.splitlines()[0] == HDR and "malformed" in p.stderr
assert commit(repo, "x", child=False).returncode == 0

# main usage error
import contextlib, io  # noqa: E402
with contextlib.redirect_stderr(io.StringIO()):
    assert gate.main([]) == 2 and gate.main(["bogus"]) == 2
print("ok")
