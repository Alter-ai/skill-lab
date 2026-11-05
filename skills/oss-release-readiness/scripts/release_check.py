"""Pre-publication check of a git repo. Usage: release_check.py <repo> [--forbid=TEXT ...]
Exit 0 clean, 1 findings, 2 not a git repo, no commits, bad usage or a git failure.
Findings never contain the forbidden text."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

MAX_BYTES = 5 * 1024 * 1024
REQUIRED = ["LICENSE", "README.md", "SECURITY.md"]


def git(repo, *args, ok=(0,)):
    r = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=repo, capture_output=True)
    if r.returncode not in ok:
        raise RuntimeError(f"git {args[0]} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8", "replace")


def sensitive(path):
    n = PurePosixPath(path).name.lower()
    return n.endswith("zone.identifier") or n == ".env" or n.startswith(".env.") or n.endswith((".pem", ".key"))


def notebook_cells(nb):
    cells = list(nb.get("cells", []))  # nbformat 4
    for ws in nb.get("worksheets", []):  # nbformat 3
        cells += ws.get("cells", [])
    return cells


def scan(repo: Path, forbid: list[str]) -> list[str]:
    first = {}
    for i, t in enumerate(forbid):
        first.setdefault(t.lower(), i)
    pat = re.compile("|".join(re.escape(t) for t in sorted(first, key=len, reverse=True)) or "(?!)", re.I)

    def red(path):  # a path may itself contain forbidden text; never echo it
        return pat.sub(lambda m: f"<forbid[{first[m.group().lower()]}]>", path)

    out = []
    head_files = {}  # path -> size at HEAD
    for rec in git(repo, "ls-tree", "-r", "-l", "-z", "HEAD").split("\0"):
        if rec:
            meta, path = rec.split("\t", 1)
            size = meta.split()[-1]
            head_files[path] = int(size) if size.isdigit() else 0  # submodules show "-"
    hist_paths = sorted({p for p in git(repo, "log", "--all", "--name-only", "--format=").splitlines() if p})
    tags = []  # raw text of annotated tags
    for ref in git(repo, "for-each-ref", "--format=%(objecttype) %(refname)", "refs/tags").splitlines():
        kind, name = ref.split(" ", 1)
        if kind == "tag":
            tags.append(git(repo, "cat-file", "tag", name).lower())

    for i, text in enumerate(forbid):
        low = text.lower()
        # grep exit 1 = no match; -S/--grep joined and -e keep a leading "-" from being read as an option
        text_hits = set()
        for line in git(repo, "grep", "-F", "-n", "-i", "-z", "-e", text, "HEAD", "--", ok=(0, 1)).split("\n"):
            if line.count("\0") >= 2:  # "Binary file ... matches" has no NUL
                path, num, _ = line.split("\0", 2)
                path = path.removeprefix("HEAD:")
                text_hits.add(path)
                out.append(f"forbid[{i}] content {red(path)}:{num}")
        for rec in git(repo, "grep", "-F", "-i", "-l", "-z", "-e", text, "HEAD", "--", ok=(0, 1)).split("\0"):
            path = rec.removeprefix("HEAD:")
            if rec and path not in text_hits:
                out.append(f"forbid[{i}] content {red(path)} binary")
        for label, args in (("history", ("-S" + text,)), ("commit-message", ("--grep=" + text,))):
            n = len(git(repo, "log", "--all", "-i", "-F", *args, "--format=%H", "--").split())
            if n:
                out.append(f"forbid[{i}] {label} {n} commits")
        n = sum(low in line.lower() for line in git(repo, "log", "--all", "--format=%ae %ce").splitlines())
        if n:
            out.append(f"forbid[{i}] author-email {n} commits")
        n = sum(low in t for t in tags)
        if n:
            out.append(f"forbid[{i}] tag {n} tags")
        n = sum(low in p.lower() for p in head_files)
        if n:
            out.append(f"forbid[{i}] path-head {n} files")
        n = sum(low in p.lower() for p in hist_paths)
        if n:
            out.append(f"forbid[{i}] path-history {n} files")

    out += [f"sensitive-path {red(p)}" for p in hist_paths if sensitive(p)]
    for path, size in sorted(head_files.items()):
        if size > MAX_BYTES:
            out.append(f"large-file {red(path)}")
        if path.endswith(".ipynb"):
            try:
                cells = notebook_cells(json.loads(git(repo, "show", f"HEAD:{path}")))
                if any(c.get("outputs") for c in cells):
                    out.append(f"notebook-output {red(path)}")
            except (ValueError, AttributeError, TypeError, RuntimeError):
                out.append(f"notebook-unreadable {red(path)}")
    out += [f"missing {f}" for f in REQUIRED if f not in head_files]

    sha = re.compile(r"upstream.*\b[0-9a-f]{40}\b", re.I)
    for d in sorted({p.split("/")[1] for p in head_files if p.startswith("skills/") and p.count("/") >= 2}):
        base = f"skills/{d}"
        if f"{base}/LICENSE" in head_files and not (
                f"{base}/SOURCE.md" in head_files
                and any(sha.search(ln) for ln in git(repo, "show", f"HEAD:{base}/SOURCE.md").splitlines())):
            out.append(f"attribution {red(base)}")
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--forbid", action="append", default=[])
    a = ap.parse_args(argv)
    if any(not f or "\n" in f or "\r" in f for f in a.forbid):
        print("error: --forbid values must be non-empty and single-line", file=sys.stderr)
        return 2
    try:
        repo = Path(git(a.repo, "rev-parse", "--show-toplevel").strip())
    except (RuntimeError, OSError):
        print(f"error: {a.repo} is not a git repo", file=sys.stderr)
        return 2
    try:
        git(repo, "rev-parse", "--verify", "-q", "HEAD")
    except RuntimeError:
        print("error: HEAD has no commits (unborn branch); check out a branch with history first", file=sys.stderr)
        return 2
    try:
        findings = scan(repo, a.forbid)
    except RuntimeError as e:
        print(f"error: {str(e)[:200]}", file=sys.stderr)
        return 2
    for f in findings:
        print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
