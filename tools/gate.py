"""Tier gate for Claude Code git commits (stdlib only)."""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import tempfile
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


def _added(repo: Path, change_path: str) -> tuple[str, int | None]:
    """(base, committer time) of the oldest commit that added the file; ("", None) if never committed."""
    lines = git(repo, "log", "--diff-filter=A", "--format=%H %ct", "--", change_path, check=False).splitlines()
    lines = [l for l in lines if l.strip()]
    if not lines:
        return "", None
    sha, ct = lines[-1].split()
    parent = git(repo, "rev-parse", "-q", "--verify", sha + "^", check=False).strip()
    return (parent or EMPTY_TREE), int(ct)


def change_base(repo: Path, change_path: str) -> str:
    base = _added(repo, change_path)[0]
    if base:
        return base
    return "HEAD" if git(repo, "rev-parse", "-q", "--verify", "HEAD", check=False).strip() else EMPTY_TREE


def architecture_ids(text: str) -> set[str]:
    return {_scalar(m.group(1)) for m in re.finditer(r"^\s*-\s+id:\s*(.+)$", section(text, "AI structured data"), re.M)}


def hunks(repo: Path, base: str) -> dict[str, list[tuple[int, int]]]:
    out: dict[str, list[tuple[int, int]]] = {}
    cur, head, prev = None, False, ""  # head: inside a file header, where "+++ " is a header and not content
    for line in git(repo, "diff", "--cached", "-U0", "--no-color", base).splitlines():
        if line.startswith("diff --git "):
            cur, head = None, True
        elif head and line.startswith("+++ ") and prev.startswith("--- "):
            name = line[4:].split(chr(9))[0]
            cur = None if name == "/dev/null" else name[2:].replace("\\", "/")
        elif line.startswith("@@"):
            head = False
            m = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", line)
            n = int(m.group(2)) if m.group(2) is not None else 1
            if cur is not None and n:
                out.setdefault(cur, []).append((int(m.group(1)), int(m.group(1)) + n - 1))
        prev = line
    return out


def _blob(repo: Path, spec: str) -> str:
    return git(repo, "rev-parse", "-q", "--verify", spec, check=False).strip()


def _list(v) -> list[str]:
    return v if isinstance(v, list) else ([v] if v else [])


def verify_done(repo: Path, change_path: str, fm: dict, body: str, cfg: dict, tier: str,
                now: float) -> list[str]:
    errors: list[str] = []
    ct = _added(repo, change_path)[1]
    base = change_base(repo, change_path)
    parts = git(repo, "diff", "--cached", "--name-status", "-M", "-z", base).split("\0")
    names, i = [], 0  # every old and new path of this change's diff
    while i < len(parts) and parts[i]:
        n = 2 if parts[i][0] in "RC" else 1
        names += [x.replace("\\", "/") for x in parts[i + 1:i + 1 + n]]
        i += n + 1
    arch = cfg["architecture"]
    arch_text = index_text(repo, arch)
    comps = _list(fm.get("components"))
    if not comps:
        errors.append("components must be non-empty")
    elif arch_text is None:
        errors.append(f"components cannot be checked: {arch} is missing, create it")
    else:
        ids = architecture_ids(arch_text)
        errors += [f"components: unknown id {c!r}" for c in comps if c not in ids]
    if section(body, "行為改變") and arch not in names:
        errors.append(f"behavior changed but {arch} was not updated in this change")
    hk = hunks(repo, base)
    for e in _list(fm.get("evidence")):
        path, _, ln = e.rpartition(":")
        if classify(path, cfg) == "doc" or path not in names or not ln.isdigit() or not any(a <= int(ln) <= b for a, b in hk.get(path, [])):
            errors.append(f"evidence {e!r} is not inside a changed hunk")
    vb = _list(fm.get("verified_by"))
    if not any(not v.startswith("manual:") and _is_test_cmd(" ".join(v.split()), cfg["test_commands"]) for v in vb):
        errors.append("verified_by needs at least one entry that matches test_commands")
    else:
        ok = [r for r in read_log(repo) if r.get("kind") == "test" and r.get("ok") is True
              and re.fullmatch(r"[0-9a-f]{40}", str(r.get("tree", "")))]
        if not ok:
            errors.append("verified_by: no successful test run recorded")
        else:
            tree = ok[-1]["tree"]
            for p in names:
                if classify(p, cfg) != "doc" and _blob(repo, ":" + p) != _blob(repo, f"{tree}:{p}"):
                    errors.append(f"verified_by: {p} changed after the last successful test run")
    if not _list(fm.get("reviewed_by")):
        errors.append("reviewed_by must be non-empty")
    elif not any(r.get("kind") == "agent" and change_path in r.get("prompt_paths", [])
                 and (ct is None or r.get("t", 0) >= ct) for r in read_log(repo)):
        errors.append("reviewed_by: no reviewer agent was dispatched for this change file")
    if tier == "T3" and not section(body, "決策"):
        errors.append("T3 change needs a non-empty 決策 section")
    return errors


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


def log_path(repo: Path) -> Path:
    return (repo / git(repo, "rev-parse", "--git-common-dir").strip()) / "agent-evidence.jsonl"


def tree_snapshot(repo: Path) -> str:
    fd, idx = tempfile.mkstemp(prefix="gate-index-")
    os.close(fd)
    os.unlink(idx)  # git creates it; an empty file is not a valid index
    env = {**os.environ, "GIT_INDEX_FILE": idx}
    try:
        if git(repo, "rev-parse", "--verify", "-q", "HEAD", check=False).strip():
            git(repo, "read-tree", "HEAD", env=env)
        git(repo, "add", "-A", env=env)
        return git(repo, "write-tree", env=env).strip()
    finally:
        Path(idx).unlink(missing_ok=True)


def append_log(repo: Path, rec: dict) -> None:
    with log_path(repo).open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_log(repo: Path) -> list[dict]:
    try:
        raw = log_path(repo).read_bytes()
    except OSError:
        return []
    out = []
    for line in raw.splitlines():
        try:
            out.append(json.loads(line.decode("utf-8")))
        except ValueError:  # UnicodeDecodeError and JSONDecodeError both subclass it
            pass
    return out


def _is_test_cmd(cmd: str, prefixes: list[str]) -> bool:
    for p in (" ".join(x.split()) for x in prefixes):
        if p and (cmd == p or cmd.startswith(p + " ") or (p.endswith("/") and cmd.startswith(p))):
            return True
    return False


PATH_RE = r"""docs/changes/[^\s'"`)\]]+\.md"""


def handle_evidence(payload: dict, now: float) -> None:
    """Record test runs and agent dispatches. Must never raise: it runs inside a tool-call hook."""
    try:
        event, tool, ti = payload.get("hook_event_name"), payload.get("tool_name"), payload.get("tool_input") or {}
        repo = repo_root(Path(payload["cwd"].replace("\\", "/")))
        cfg = load_config(repo) if repo else None
        if cfg is None:
            return
        if tool in ("Bash", "PowerShell"):
            cmd = " ".join(str(ti.get("command", "")).split())
            if _is_test_cmd(cmd, cfg["test_commands"]):
                append_log(repo, {"t": now, "kind": "test", "ok": event == "PostToolUse", "cmd": cmd,
                                  "tree": tree_snapshot(repo)})
        elif tool == "Agent" and event == "PostToolUse":
            paths = list(dict.fromkeys(re.findall(PATH_RE, ti.get("prompt", ""))))
            append_log(repo, {"t": now, "kind": "agent", "agent_type": ti.get("subagent_type", ""),
                              "prompt_paths": paths})
    except Exception:
        return


SEP_RE = re.compile(r"^[;&|]+$")
SESSION_RE = re.compile(r"(unset|Remove-Item)\s+\S*CLAUDE_CODE_CHILD_SESSION|-u\s+CLAUDE_CODE_CHILD_SESSION"
                        r"|CLAUDE_CODE_CHILD_SESSION\s*=")
BANNED_SUBS = {"cherry-pick", "revert", "rebase", "am", "commit-tree", "update-ref"}
ARG_FLAGS = "mFCcStu"  # short flags that consume the rest of the cluster as their value


def _invocations(command: str) -> list[list[str]]:
    out: list[list[str]] = []
    for line in command.splitlines():
        try:
            toks = list(shlex.shlex(line, posix=True, punctuation_chars=True))
        except ValueError:
            toks = line.split()
        cur: list[str] = []
        for t in toks:
            if SEP_RE.match(t):
                out.append(cur)
                cur = []
            else:
                cur.append(t)
        out.append(cur)
    return [c for c in out if c]


def _git_sub(inv: list[str]) -> tuple[str, list[str]] | None:
    """(subcommand, args) of the git call in one invocation, skipping global options."""
    i = next((i for i, t in enumerate(inv) if t.replace("\\", "/").rsplit("/", 1)[-1].lower() in ("git", "git.exe")), None)
    if i is None:
        return None
    i += 1
    while i < len(inv) and inv[i].startswith("-"):
        i += 2 if inv[i] in ("-c", "-C", "--git-dir", "--work-tree", "--namespace", "--exec-path") else 1
    return (inv[i], inv[i + 1:]) if i < len(inv) else None


def check_pretool(command: str) -> str | None:
    if re.search(r"hookspath", command, re.I):
        return "core.hooksPath must not be set"
    if SESSION_RE.search(command) or ("SetEnvironmentVariable" in command and "CLAUDE_CODE_CHILD_SESSION" in command):
        return "CLAUDE_CODE_CHILD_SESSION must not be unset or changed"
    for inv in _invocations(command):
        g = _git_sub(inv)
        if g is None:
            continue
        sub, args = g
        if "env" in inv and ("-i" in inv or "--ignore-environment" in inv):
            return "env -i hides CLAUDE_CODE_CHILD_SESSION from git"
        if sub in BANNED_SUBS:
            return f"git {sub} bypasses the commit-msg hook"
        if sub in ("commit", "merge") and "--no-verify" in args:
            return f"git {sub} --no-verify bypasses hooks"
        if sub == "commit":
            for a in args:
                if a.startswith("-") and not a.startswith("--"):
                    for ch in a[1:]:
                        if ch == "n":
                            return "git commit -n bypasses hooks"
                        if ch in ARG_FLAGS:
                            break
    return None


def retro_warning(repo: Path) -> str | None:
    added = git(repo, "log", "--diff-filter=A", "--format=%H", "--", ".agent-gate", check=False).split()
    if not added:
        return None
    ack_file = repo / git(repo, "rev-parse", "--git-common-dir").strip() / "gate-ack"
    ack = set(ack_file.read_text(encoding="utf-8").split()) if ack_file.is_file() else set()
    miss = []
    for h in git(repo, "log", "--format=%H", f"{added[-1]}..HEAD").split():
        msg = git(repo, "show", "-s", "--format=%B", h)
        if not TIER_RE.search(msg.replace("\r\n", "\n")) and h not in ack and h[:7] not in ack:
            miss.append(h[:7])
    if not miss:
        return None
    return ("gate: commits without a Tier trailer since .agent-gate was added: " + ", ".join(miss)
            + ". Acknowledge by adding the hash to .git/gate-ack.")


def handle_pretool(payload: dict) -> tuple[int, str]:
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return 0, ""
    cmd = str((payload.get("tool_input") or {}).get("command", ""))
    repo = repo_root(Path(str(payload.get("cwd", ".")).replace("\\", "/")))
    if repo is None or not (repo / ".agent-gate").is_file():
        return 0, ""
    try:
        load_config(repo)
    except tomllib.TOMLDecodeError:
        if re.search(r"\bgit\b", cmd):
            return 2, "gate: blocked (see skill change-record)\n.agent-gate is malformed; fix it first"
        return 0, ""
    reason = check_pretool(cmd)
    if reason:
        return 2, "gate: blocked (see skill change-record)\n" + reason
    if any((g := _git_sub(i)) and g[0] in ("commit", "merge") for i in _invocations(cmd)):
        text = retro_warning(repo)
        if text:
            return 0, json.dumps({"systemMessage": text}, ensure_ascii=False)
    return 0, ""
