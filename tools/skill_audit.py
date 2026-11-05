"""Static checks for SKILL.md files: size, frontmatter limits, dangling references, pairwise line overlap.

usage: python tools/skill_audit.py [prefix=skills_dir ...] [--overlap PCT] [--json]
Limits follow the Agent Skills spec and the Claude Code skills docs (read 2026-11-03).
Exit code 1 when any skill is flagged, so it can gate a commit or CI.
"""
import itertools
import json
import re
import sys
from pathlib import Path

MAX_LINES = 500
MAX_BYTES = 20 * 1024  # shortcut: ~5,000 tokens at ~4 bytes/token; swap in a real tokenizer if this is disputed
MAX_NAME, MAX_DESC = 64, 1024
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REF_RE = re.compile(r"(?<![\w/.-])([a-z][a-z0-9-]*):([a-z][a-z0-9-]*)\b")  # plugin:skill
FILE_RE = re.compile(r"\]\((?!https?:|#|mailto:)([^)\s]+)\)|`((?:scripts|references|assets|templates)/[^`\s]+)`")

# shortcut: only the ponytail marketplace path is stable; other plugin roots are hashed, so pass them as prefix=dir
DEFAULT_ROOTS = {"ponytail": Path.home() / ".claude" / "plugins" / "marketplaces" / "ponytail" / "skills"}


def load(path):
    t = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n?(.*)", t, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", t)

    def val(key):
        mm = re.search(rf"^{key}:[ \t]*(.*(?:\n[ \t]+.*)*)", fm, re.M)
        if not mm:
            return ""
        v = re.sub(r"^[>|][-+]?\s*", "", mm.group(1).strip())
        return " ".join(x.strip() for x in v.splitlines()).strip("\"'")

    return dict(path=path, dir=path.parent.name, has_fm=bool(m), lines=t.count("\n") + 1,
                bytes=len(t.encode()), name=val("name"), desc=val("description"), body=body)


def load_all(roots):
    out = {}
    for prefix, root in roots.items():
        for p in sorted(Path(root).glob("*/SKILL.md")):
            out[f"{prefix}:{p.parent.name}"] = load(p)
    return out


def flags(s, known):
    f = []
    if not s["has_fm"]:
        f.append("no-frontmatter")
    if s["lines"] > MAX_LINES:
        f.append(f"lines>{MAX_LINES}")
    if s["bytes"] > MAX_BYTES:
        f.append("bytes>20KB")
    if not s["desc"]:
        f.append("no-description")
    if len(s["desc"]) > MAX_DESC:
        f.append(f"desc>{MAX_DESC}")
    if len(s["name"]) > MAX_NAME or not NAME_RE.match(s["name"]):
        f.append("bad-name")
    if s["name"] != s["dir"]:
        f.append("name!=dir")
    prefixes = {k.split(":")[0] for k in known}
    for pre, nm in REF_RE.findall(s["body"]):
        # unknown prefixes only count when both halves are hyphenated, which skips XML (w:author) and path:line noise
        if f"{pre}:{nm}" not in known and (pre in prefixes or ("-" in pre and "-" in nm)):
            f.append(f"ref?{pre}:{nm}")
    for a, b in FILE_RE.findall(s["body"]):
        rel = (a or b).split("#")[0]
        if rel and not re.search(r"[*<>{}]", rel) and not (s["path"].parent / rel).exists():
            f.append(f"missing-file:{rel}")
    return sorted(set(f))


def overlap(skills, pct):
    sets = {k: {x.strip() for x in s["body"].splitlines() if len(x.strip()) >= 25} for k, s in skills.items()}
    rows = []
    for a, b in itertools.combinations(sorted(sets), 2):
        small = min(len(sets[a]), len(sets[b]))
        shared = len(sets[a] & sets[b])
        if small and shared / small * 100 >= pct:
            rows.append((shared / small * 100, shared, small, a, b))
    return sorted(rows, reverse=True)


def main(argv):
    roots, pct, as_json = {}, 30.0, False
    it = iter(argv)
    for a in it:
        if a == "--overlap":
            pct = float(next(it))
        elif a == "--json":
            as_json = True
        elif "=" in a:
            k, v = a.split("=", 1)
            roots[k] = Path(v)
        else:
            sys.exit(__doc__)
    skills = load_all(roots or DEFAULT_ROOTS)
    known = {f"{k.split(':')[0]}:{s['name']}" for k, s in skills.items()} | set(skills)
    if as_json:
        rows = [{"skill": k, "lines": s["lines"], "bytes": s["bytes"], "name_len": len(s["name"]),
                 "desc_len": len(s["desc"]), "flags": flags(s, known)} for k, s in sorted(skills.items())]
        pairs = [{"pct": p, "shared": sh, "smaller": sm, "a": a, "b": b} for p, sh, sm, a, b in overlap(skills, pct)]
        bad = sum(bool(r["flags"]) for r in rows)
        print(json.dumps({"skills": rows, "flagged": bad, "overlap": pairs}, ensure_ascii=False, indent=2))
        return 1 if bad else 0
    bad = 0
    print("skill | lines | KB | name | desc | flags")
    for k, s in sorted(skills.items(), key=lambda kv: -kv[1]["bytes"]):
        fl = flags(s, known)
        bad += bool(fl)
        print(f"{k} | {s['lines']} | {s['bytes'] / 1024:.1f} | {len(s['name'])} | {len(s['desc'])} | {', '.join(fl)}")
    print(f"\n{len(skills)} skills, {bad} flagged, total description chars {sum(len(s['desc']) for s in skills.values())}")
    print(f"\nbody overlap >= {pct:.0f}% (shared lines >= 25 chars / smaller skill):")
    for p, sh, sm, a, b in overlap(skills, pct):
        print(f"{p:.0f}% {sh}/{sm}  {a} <> {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
