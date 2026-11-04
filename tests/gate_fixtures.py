"""Temp git repo helpers for gate tests."""
import subprocess
import tempfile
from pathlib import Path

DEFAULT_GATE = 'test_commands = ["python -I tests"]\n'


def run(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True)
    return r.stdout.decode("utf-8")


def write(repo: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))


def make_repo(files: dict[str, str], gate: str | None = DEFAULT_GATE, commit: bool = True) -> Path:
    repo = Path(tempfile.mkdtemp(prefix="gate-test-"))
    run(repo, "init", "-q")
    for k, v in (("user.name", "t"), ("user.email", "t@example.com"), ("core.autocrlf", "false")):
        run(repo, "config", k, v)
    if gate is not None:
        write(repo, {".agent-gate": gate})
    write(repo, files)
    if commit:
        run(repo, "add", "-A")
        run(repo, "commit", "-q", "-m", "init")
    return repo


def stage(repo: Path, files: dict[str, str]) -> None:
    write(repo, files)
    run(repo, "add", "--", *files)
