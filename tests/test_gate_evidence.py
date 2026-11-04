"""Self-check for tools/gate.py evidence log. Run: python -I tests/test_gate_evidence.py"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
from gate_fixtures import make_repo, run  # noqa: E402


def bash(repo, cmd, event="PostToolUse", tool="Bash"):
    return {"hook_event_name": event, "tool_name": tool, "tool_input": {"command": cmd},
            "cwd": str(repo).replace("/", "\\")}


repo = make_repo({"a.txt": "a"}, gate='test_commands = ["pytest", "tests/"]\n')
gate.handle_evidence(bash(repo, "pytest  -q"), 100.0)
recs = gate.read_log(repo)
assert len(recs) == 1, recs
assert recs[0] == {"t": 100.0, "kind": "test", "ok": True, "cmd": "pytest -q", "tree": gate.tree_snapshot(repo)}, recs
gate.handle_evidence(bash(repo, "pytest", "PostToolUseFailure", "PowerShell"), 101.0)
assert gate.read_log(repo)[1]["ok"] is False
gate.handle_evidence(bash(repo, "tests/run.sh"), 102.0)   # prefix ending in "/"
gate.handle_evidence(bash(repo, "pytestx"), 103.0)         # not a word boundary
gate.handle_evidence(bash(repo, "ls"), 104.0)
assert len(gate.read_log(repo)) == 3

gate.handle_evidence({"hook_event_name": "PostToolUse", "tool_name": "Agent", "cwd": str(repo),
                      "tool_input": {"prompt": "see docs/changes/2026-01-01-x.md and `docs/changes/2026-01-01-x.md`, docs/changes/b.md)",
                                     "subagent_type": "reviewer"}}, 105.0)
assert gate.read_log(repo)[-1] == {"t": 105.0, "kind": "agent", "agent_type": "reviewer",
                                   "prompt_paths": ["docs/changes/2026-01-01-x.md", "docs/changes/b.md"]}
n = len(gate.read_log(repo))
gate.handle_evidence({"hook_event_name": "PostToolUseFailure", "tool_name": "Agent", "cwd": str(repo),
                      "tool_input": {"prompt": "x"}}, 106.0)
gate.handle_evidence({"hook_event_name": "PostToolUse", "tool_name": "Read", "cwd": str(repo),
                      "tool_input": {}}, 107.0)
assert len(gate.read_log(repo)) == n

# no .agent-gate -> no record
plain = make_repo({"a.txt": "a"}, gate=None)
gate.handle_evidence(bash(plain, "pytest"), 1.0)
assert gate.read_log(plain) == []

# malformed .agent-gate -> no exception, no record
bad = make_repo({"a.txt": "a"}, gate="test_commands = [\n")
gate.handle_evidence(bash(bad, "pytest"), 1.0)
assert gate.read_log(bad) == []

# no HEAD: tree_snapshot works and sees untracked files
nohead = make_repo({"a.txt": "a"}, commit=False)
t = gate.tree_snapshot(nohead)
assert len(t) == 40 and t == gate.tree_snapshot(nohead)
assert not (nohead / ".git" / "index").exists()  # real index untouched

# snapshot tracks content, including unstaged edits
(repo / "a.txt").write_text("b")
assert gate.tree_snapshot(repo) != recs[0]["tree"]

# worktree and main share a log path
wt = Path(tempfile.mkdtemp(prefix="gate-wt-")) / "wt"
run(repo, "worktree", "add", "-q", str(wt), "-b", "side")
assert gate.log_path(wt).resolve() == gate.log_path(repo).resolve()
assert gate.log_path(repo).name == "agent-evidence.jsonl"

# read_log: missing file -> [], undecodable lines skipped
p = gate.log_path(repo)
with p.open("ab") as f:
    f.write(b"\xff\xfe garbage\n{not json\n")
gate.handle_evidence(bash(repo, "pytest"), 200.0)
assert gate.read_log(repo)[-1]["t"] == 200.0
p.unlink()
assert gate.read_log(repo) == []
print("ok")
