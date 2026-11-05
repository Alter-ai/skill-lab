"""Pre-publication check of a git repo. Usage: release_check.py <repo> [--forbid=TEXT ...]
Exit 0 clean, 1 findings, 2 not a git repo or no commits. Findings never contain the forbidden text."""
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
    n = PurePosixPath(path).name
    return n.endswith("Zone.Identifier") or n == ".env" or n.endswith((".pem", ".key"))


def scan(repo: Path, forbid: list[str]) -> list[str]:
    out = []
    for i, text in enumerate(forbid):
        # grep exit 1 = no match; -S joined and -e keep a leading "-" from being read as an option
        for line in git(repo, "grep", "-F", "-n", "-i", "-I", "-z", "-e", text, "HEAD", "--", ok=(0, 1)).split("\n"):
            if line:
                path, num, _ = line.split("\0", 2)
                out.append(f"forbid[{i}] content {path.removeprefix('HEAD:')}:{num}")
        n = len(git(repo, "log", "--all", "-i", "-F", f"-S{text}", "--format=%H", "--").split())
        if n:
            out.append(f"forbid[{i}] history {n} commits")
        low = text.lower()
        n = sum(low in line.lower() for line in git(repo, "log", "--all", "--format=%ae %ce").splitlines())
        if n:
            out.append(f"forbid[{i}] author-email {n} commits")

    seen = set(git(repo, "log", "--all", "--name-only", "--format=").splitlines())
    out += [f"sensitive-path {p}" for p in sorted(seen) if p and sensitive(p)]

    files = {}  # path -> size at HEAD
    for rec in git(repo, "ls-tree", "-r", "-l", "-z", "HEAD").split("\0"):
        if rec:
            meta, path = rec.split("\t", 1)
            files[path] = int(meta.split()[-1])
    for path, size in sorted(files.items()):
        if size > MAX_BYTES:
            out.append(f"large-file {path}")
        if path.endswith(".ipynb"):
            try:
                cells = json.loads(git(repo, "show", f"HEAD:{path}")).get("cells", [])
                if any(c.get("outputs") for c in cells):
                    out.append(f"notebook-output {path}")
            except (ValueError, AttributeError, RuntimeError):
                pass  # unreadable notebook: nothing to flag
    out += [f"missing {f}" for f in REQUIRED if f not in files]

    sha = re.compile(r"upstream.*\b[0-9a-f]{40}\b", re.I)
    for d in sorted({p.split("/")[1] for p in files if p.startswith("skills/") and p.count("/") >= 2}):
        base = f"skills/{d}"
        if f"{base}/LICENSE" in files and not (
                f"{base}/SOURCE.md" in files
                and any(sha.search(ln) for ln in git(repo, "show", f"HEAD:{base}/SOURCE.md").splitlines())):
            out.append(f"attribution {base}")
    # a path may itself contain the forbidden text; never echo it
    for i, text in enumerate(forbid):
        out = [re.sub(re.escape(text), f"<forbid[{i}]>", f, flags=re.I) for f in out]
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--forbid", action="append", default=[])
    a = ap.parse_args(argv)
    repo = Path(a.repo)
    try:
        git(repo, "rev-parse", "--git-dir")
    except (RuntimeError, OSError):
        print(f"error: {a.repo} is not a git repo", file=sys.stderr)
        return 2
    try:
        git(repo, "rev-parse", "--verify", "-q", "HEAD")
    except RuntimeError:
        print("error: HEAD has no commits (unborn branch); check out a branch with history first", file=sys.stderr)
        return 2
    findings = scan(repo, a.forbid)
    for f in findings:
        print(f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
