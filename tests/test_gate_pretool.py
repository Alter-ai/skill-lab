"""Self-check for tools/gate.py pretool. Run: python -I tests/test_gate_pretool.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
from gate_fixtures import make_repo, run, write  # noqa: E402

BLOCK = [
    "git commit --no-verify -m x", "git commit -nm x", "git commit -n -m x",
    "git -c core.hooksPath=/dev/null commit -m x", "git config core.hooksPath /x",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=x git commit",
    "unset CLAUDE_CODE_CHILD_SESSION; git commit -m x", "env -u CLAUDE_CODE_CHILD_SESSION git commit",
    "$env:CLAUDE_CODE_CHILD_SESSION=''; git commit", "CLAUDE_CODE_CHILD_SESSION= git commit -m x",
    "Remove-Item Env:CLAUDE_CODE_CHILD_SESSION; git commit",
    "[Environment]::SetEnvironmentVariable('CLAUDE_CODE_CHILD_SESSION', $null)",
    "env -i git commit -m x", "git cherry-pick abc", "git revert HEAD", "git rebase main", "git am x.patch",
    "git commit-tree t", "git update-ref refs/heads/x y", "git -C /r rebase main",
    "git add . && git commit --no-verify -m x", "git merge --no-verify feature",
    "echo hi\ngit rebase main",
    "git commit --no-verif -m x", "git commit --no-v -m x", "bash -c 'git commit --no-verify -m x'",
    'powershell -Command "git commit --no-verify"', "powershell -Command git rebase main",
    "pwsh -Command git rebase main", "cmd /c git rebase main", 'sh -c "git cherry-pick x"',
    "env --unset=CLAUDE_CODE_CHILD_SESSION git commit -m x", "env -u CLAUDE_CODE_CHILD_SESSION git commit -m x",
    "unset -v CLAUDE_CODE_CHILD_SESSION", "Set-Item Env:CLAUDE_CODE_CHILD_SESSION ''",
    "export GIT_CONFIG_KEY_0=core.hooksPath", "(git rebase main)", "{ git rebase main; }",
    "git commit -m x -n", "git commit -S -n -m x", "git commit -u -n -m x", "git commit -m x -S -n", "git rebase --continue", "git rebase --skip", "git cherry-pick --continue",
]
ALLOW = [
    "git log --grep commit", "git show HEAD", 'git commit -m "fix -n flag parsing"', "ls -n",
    "git merge -n feature", "echo $CLAUDE_CODE_CHILD_SESSION", "git commit -m 'it'\"'\"'s' -m note",
    "git commit -mnote", 'git commit -m "- x"', 'git commit -m x -m "- y"', "git -C /r status", "grep hooksPath x", 'echo "CLAUDE_CODE_CHILD_SESSION=1"',
    "echo git rebase main", "git commit -m 'unset CLAUDE_CODE_CHILD_SESSION core.hooksPath'",
    "git commit -m \"$(cat <<'EOF'\nfix: core.hooksPath and unset CLAUDE_CODE_CHILD_SESSION\n"
    "git rebase main is now blocked\nEOF\n)\"",
    'git commit -m "feat: x" -m "- handle empty input"', 'git commit -m "-no longer crashes"',
    "git commit --message -nope", "bash -c ''", "bash ''", "git rebase --abort", "git cherry-pick --abort",
    "git revert --quit", "git am --abort", "git rebase --help", "git am --quit",
    "git commit -F - <<-EOF\n\tgit commit --no-verify\n\tEOF", "cat <<<'git rebase'",
]
for c in BLOCK:
    assert gate.check_pretool(c), c
for c in ALLOW:
    assert gate.check_pretool(c) is None, c

# retro_warning
repo = make_repo({"a.txt": "a"})
assert gate.retro_warning(repo) is None
write(repo, {"a.txt": "b"})
run(repo, "commit", "-qam", "no trailer")
h = run(repo, "rev-parse", "HEAD").strip()
w = gate.retro_warning(repo)
assert w and h[:7] in w, w
write(repo, {"a.txt": "c"})
run(repo, "commit", "-qam", "ok\n\nTier: T1")
assert h[:7] in gate.retro_warning(repo)
(repo / ".git" / "gate-ack").write_text(h + "\n")
assert gate.retro_warning(repo) is None

# gate-ack written by PowerShell 5.1 (UTF-16LE + BOM) and by UTF-8 with BOM
(repo / ".git" / "gate-ack").write_bytes(b"\xff\xfe" + (h + "\r\n").encode("utf-16-le"))
assert gate.retro_warning(repo) is None
(repo / ".git" / "gate-ack").write_bytes(b"\xef\xbb\xbf" + h.encode() + b"\r\n")
assert gate.retro_warning(repo) is None

# handle_pretool
def pl(cmd, cwd, tool="Bash"):
    return {"tool_name": tool, "tool_input": {"command": cmd}, "cwd": str(cwd).replace("/", "\\")}


(repo / ".git" / "gate-ack").unlink()
code, out = gate.handle_pretool(pl("git commit --no-verify", repo))
assert code == 2 and out.startswith("gate: blocked (see skill change-record)\n"), (code, out)
code, out = gate.handle_pretool(pl("git commit -m x", repo))
assert code == 0 and h[:7] in json.loads(out)["systemMessage"], out
assert gate.handle_pretool(pl("git status", repo)) == (0, "")
assert gate.handle_pretool(pl("git commit --no-verify", repo, "Read")) == (0, "")
plain = make_repo({"a.txt": "a"}, gate=None)
assert gate.handle_pretool(pl("git commit --no-verify", plain)) == (0, "")
bad = make_repo({"a.txt": "a"}, gate="test_commands = [\n")
code, out = gate.handle_pretool(pl("git commit -m x", bad))
assert code == 2 and ".agent-gate" in out, out
assert gate.handle_pretool(pl("ls", bad)) == (0, "")
print("ok")
