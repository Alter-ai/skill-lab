"""Tier gate for Claude Code git commits (stdlib only)."""
import fnmatch
import re
import subprocess
import time
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
            or any(fnmatch.fnmatch(path, g) or (g.startswith("**/") and fnmatch.fnmatch(path, g[3:]))
                   for g in cfg["sensitive"]))


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


def _scalar(v: str) -> str:
    v = v.strip()
    if v and v[0] in "\"'":
        end = v.find(v[0], 1)
        if end > 0:
            return v[1:end]
    return re.split(r"\s+#", v, maxsplit=1)[0].strip()


def parse_front_matter(text: str) -> tuple[dict, str]:
    # shortcut: flat key/scalar/list subset of YAML only, upgrade if change files need nesting
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            break
    else:
        return {}, text
    fm: dict = {}
    key = None
    for line in lines[1:end]:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- ") and key is not None and isinstance(fm[key], list):
            fm[key].append(_scalar(s[2:]))
            continue
        k, _, v = line.partition(":")
        key, v = k.strip(), _scalar(v)
        if v.startswith("[") and v.endswith("]"):
            fm[key] = [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
        else:
            fm[key] = [] if v == "" else v
    return fm, "".join(lines[end + 1:])


def section(body: str, heading_prefix: str) -> str:
    out, on = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            if on:
                break
            on = line.startswith("## " + heading_prefix)
        elif on:
            out.append(line)
    return "\n".join(out).strip()


EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
STATUSES = {"proposed", "partial", "done", "abandoned"}
TIER_RE = re.compile(r"^Tier: (T[0-3])$", re.M)
CHANGE_RE = re.compile(r"^Change: (docs/changes/\S+\.md)$", re.M)


def staged3(repo: Path) -> list[tuple[str, str, str]]:
    """(status, new path, old path); old == new unless renamed/copied."""
    base = "HEAD" if git(repo, "rev-parse", "-q", "--verify", "HEAD", check=False).strip() else EMPTY_TREE
    parts = git(repo, "diff", "--cached", "--name-status", "-M", "-z", base).split("\0")
    out, i = [], 0
    while i < len(parts) and parts[i]:
        st = parts[i]
        n = 2 if st[0] in "RC" else 1  # rename/copy carry old and new path; keep the new one
        out.append((st, parts[i + n].replace("\\", "/"), parts[i + 1].replace("\\", "/")))
        i += n + 1
    return out


def staged(repo: Path) -> list[tuple[str, str]]:
    return [(st, p) for st, p, _ in staged3(repo)]


def index_text(repo: Path, path: str) -> str | None:
    try:
        return git(repo, "show", f":{path}")
    except subprocess.CalledProcessError:
        return None


def open_changes(repo: Path) -> list[str]:
    out = []
    for p in git(repo, "ls-files", "-z", "--", "docs/changes").split("\0"):
        if p.endswith(".md") and p.count("/") == 2:
            fm, _ = parse_front_matter(index_text(repo, p) or "")
            if fm.get("status") in ("proposed", "partial"):
                out.append(p)
    return out


def verify_done(repo: Path, change_path: str, fm: dict, body: str, cfg: dict, tier: str,
                now: float) -> list[str]:
    return []  # Task 5


def check_commit(repo: Path, msg: str, cfg: dict) -> list[str]:
    msg = "\n".join(l for l in msg.replace("\r\n", "\n").split("\n") if not l.startswith("#"))
    m = TIER_RE.search(msg)
    if not m:
        return ["missing 'Tier: T0|T1|T2|T3' trailer in commit message"]
    tier = m.group(1)
    if git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).strip():
        return []
    files = staged3(repo)
    cm = CHANGE_RE.search(msg)
    errors: list[str] = []
    if cm:
        path = cm.group(1)
        text = index_text(repo, path)
        if text is None:
            return [f"Change file not found in index: {path}"]
        fm, body = parse_front_matter(text)
        if fm.get("status") not in STATUSES:
            errors.append(f"{path}: status must be one of {sorted(STATUSES)}")
        if fm.get("tier") not in ("T2", "T3"):
            errors.append(f"{path}: change tier must be T2 or T3")
        if fm.get("tier") != tier:
            errors.append(f"{path}: tier {fm.get('tier')!r} does not match commit Tier {tier}")
        if fm.get("status") == "done":
            errors += verify_done(repo, path, fm, body, cfg, tier, time.time())
    elif tier in ("T2", "T3"):
        return [f"Tier {tier} requires a 'Change: docs/changes/<name>.md' trailer"]
    if tier in ("T2", "T3"):
        return errors
    kinds = [(st, p, classify(p, cfg)) for st, p, _ in files]
    if any("high" in (classify(o, cfg), k) for (_, _, o), (_, _, k) in zip(files, kinds)):
        errors.append("sensitive or high-risk path staged: this looks like T2")
    if tier == "T0":
        if any(st != "R100" and k in ("source", "test") for st, _, k in kinds):
            errors.append("T0 allows only docs/config changes or pure renames: this looks like T2")
    else:
        if any(st.startswith("A") and k == "source" for st, _, k in kinds):
            errors.append("T1 cannot add a source file: this looks like T2")
        if sum(k == "source" and (st[0] in "MD" or (st[0] == "R" and st != "R100")) for st, _, k in kinds) > 1:
            errors.append("T1 allows at most one modified source file: this looks like T2")
    if not cm and any(k in ("source", "test") for _, _, k in kinds) and (oc := open_changes(repo)):
        errors.append(f"open change {oc[0]} exists: add a 'Change:' trailer")
    return errors
