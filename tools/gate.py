"""Tier gate for Claude Code git commits (stdlib only)."""
import fnmatch
import subprocess
import tomllib
from pathlib import Path, PurePosixPath

DEFAULT_ARCH = "docs/architecture/ARCHITECTURE.md"
HIGH_NAMES = {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", ".agent-gate",
              "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs"}
DOC_EXTS = {".md", ".rst", ".txt"}
CONFIG_EXTS = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}


def git(repo: Path, *args: str, env: dict | None = None, check: bool = True) -> str:
    r = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=repo, env=env,
                       capture_output=True, check=check)
    return r.stdout.decode("utf-8", errors="replace")


def repo_root(cwd: Path) -> Path | None:
    try:
        return Path(git(cwd, "rev-parse", "--show-toplevel").strip())
    except (subprocess.CalledProcessError, OSError):
        return None


def load_config(repo: Path) -> dict | None:
    f = repo / ".agent-gate"
    if not f.is_file():
        return None
    raw = tomllib.loads(f.read_text(encoding="utf-8"))
    return {"test_commands": raw.get("test_commands", []), "sensitive": raw.get("sensitive", []),
            "architecture": raw.get("architecture", DEFAULT_ARCH)}


def is_high(path: str, name: str, cfg: dict) -> bool:
    return (name in HIGH_NAMES or name.endswith(".lock")
            or (name.startswith("requirements") and name.endswith(".txt"))
            or path.startswith((".github/workflows/", ".claude/"))
            or any(fnmatch.fnmatch(path, g) for g in cfg["sensitive"]))


def is_test(parts: tuple, name: str) -> bool:
    stem = name.rsplit(".", 1)[0]
    return (bool(TEST_DIRS & set(parts[:-1])) or name.startswith("test_") or stem.endswith("_test")
            or ".test." in name or ".spec." in name)


def classify(path: str, cfg: dict) -> str:
    path = path.replace("\\", "/")
    p = PurePosixPath(path)
    if is_high(path, p.name, cfg):
        return "high"
    if is_test(p.parts, p.name):
        return "test"
    if p.suffix in DOC_EXTS or p.parts[0] == "docs":
        return "doc"
    if p.suffix in CONFIG_EXTS:
        return "config"
    return "source"
