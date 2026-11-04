"""Self-check for tools/gate.py classify/load_config. Run: python -I tests/test_gate_classify.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gate  # noqa: E402

cfg = {"test_commands": [], "sensitive": ["**/auth/**"], "architecture": "docs/architecture/ARCHITECTURE.md"}
assert gate.classify("", cfg) == "source"
assert gate.classify("README.md", cfg) == "doc"
assert gate.classify("docs/x.py", cfg) == "doc"
assert gate.classify("notes.txt", cfg) == "doc"
assert gate.classify("conf/app.yaml", cfg) == "config"
for p in [".github/workflows/ci.yml", ".github/CODEOWNERS", ".github/dependabot.yml", ".gitlab-ci.yml",
          ".circleci/config.yml", "package.json", "pyproject.toml", "requirements-dev.txt",
          "Cargo.toml", "go.mod", "uv.lock", "pnpm-lock.yaml", ".claude/settings.json", ".agent-gate",
          "src/auth/login.py", r"src\auth\login.py"]:
    assert gate.classify(p, cfg) == "high", p
for p in ["tests/a.py", "src/__tests__/b.ts", "test_x.py", "x_test.go", "a.test.ts", "a.spec.ts", "spec/a.rb"]:
    assert gate.classify(p, cfg) == "test", p
assert gate.classify("auth/x.py", cfg) == "high"
assert gate.classify("payments/a.py", {**cfg, "sensitive": ["**/payments/**"]}) == "high"
assert gate.classify("rea/bridge/pwndbg/inspect.py", cfg) == "source"
assert gate.classify("src/中文 檔.py", cfg) == "source"

with tempfile.TemporaryDirectory() as t:
    r = Path(t)
    assert gate.load_config(r) is None
    (r / ".agent-gate").write_text('test_commands = ["pytest"]\n', encoding="utf-8")
    c = gate.load_config(r)
    assert c == {"test_commands": ["pytest"], "sensitive": [],
                 "architecture": "docs/architecture/ARCHITECTURE.md"}, c
    assert gate.repo_root(r) is None or gate.repo_root(r) != r  # temp dir is not its own repo

print("ok")
