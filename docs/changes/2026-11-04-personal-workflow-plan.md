# 自用工作流 gate 實作計畫

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal：** 依 r2 spec 做出 tier gate（git commit-msg hook、薄 PreToolUse、證據日誌）與配套的 skill／CLAUDE.md 改動，並先在 skill-lab 自己身上試用。

**Architecture：** `tools/gate.py` 是單一檔案，有四個子指令：`install`、`commit-msg`、`pretool`、`evidence`。做成單一檔案是為了部署時只要複製一個檔。git 的 commit-msg hook 和 Claude Code 的 hook 都呼叫它。其餘工作是改 skill 的 Markdown 和 eval 的資料。

**Tech Stack：** Python 3.13 標準函式庫（`tomllib`、`subprocess`、`json`、`fnmatch`）、git 2.56、Claude Code hooks。

**Spec：** [2026-11-04-personal-workflow-design.md](2026-11-04-personal-workflow-design.md)（r2）

## Global Constraints

- 只用標準函式庫，不加任何依賴。執行一律用 `C:/Python313/python.exe -I`。
- 測試沿用 skill-lab 的慣例：一個測試檔就是一支 assert 腳本，用 `python -I tests/<file>.py` 執行，成功時印出 `ok`。
- gate 只在 repo 根目錄有 `.agent-gate` 時作用，否則一律 exit 0。
- 判斷是 Claude 執行的唯一依據是 `os.environ.get("CLAUDE_CODE_CHILD_SESSION") == "1"`，不要讀 `CLAUDECODE`。
- 所有 git 呼叫都帶 `-c core.quotePath=false`，路徑清單一律用 `-z`。路徑在比較前先轉成正斜線。
- hook 指令一律寫絕對路徑：`C:/Python313/python.exe -I <home>/.claude/hooks/gate.py <subcommand>`。
- Tier trailer 的正規式是 `^Tier: (T[0-3])$`，Change trailer 的正規式是 `^Change: (docs/changes/\S+\.md)$`，兩者都是多行模式。
- `status` 的合法值：`proposed`、`partial`、`done`、`abandoned`。
- ARCHITECTURE.md 的位置：讀 `.agent-gate` 的 `architecture` 鍵，預設值 `docs/architecture/ARCHITECTURE.md`。這是 c4-architecture skill 的慣例，spec 簡寫成 `ARCHITECTURE.md`。
- 個人 skill 只改 `skills/` 底下的原始檔，部署是最後一個 task。
- 擋下時 stderr 第一行固定寫 `gate: blocked (see skill change-record)`，接著每行列一個原因。

## Review Focus

1. **repo 還沒有任何 commit（沒有 HEAD）**：`diff --cached`、`read-tree HEAD`、`git log` 都必須能運作。比較基準改用 empty tree `4b825dc642cb6eb9a060e54bf8d69288fbee4904`。測試放在 Task 3、Task 4。
2. **中文或含空白的檔名**：必須正確分類、正確比對 blob。測試放在 Task 3。
3. **CRLF**：Windows 上 change 檔和 commit message 的換行可能是 `\r\n`，trailer 和 front matter 都要能解析。測試放在 Task 2、Task 3。
4. **merge commit**：commit-msg 也會在 merge 時執行。只要存在 `MERGE_HEAD`，就**只檢查 Tier trailer**，跳過分類和 change 檔檢查。被 merge 進來的 commit 已經各自檢查過，這是本計畫補上的決定。測試放在 Task 3。
5. **成功的測試之後又跑了一次失敗的測試**：spec 寫的是取「最後一次**成功**」的紀錄，所以這種情況會放行。照 spec 實作，但要有一個測試把這個行為釘住，並在 change 檔的「已知限制」記上一筆。測試放在 Task 5。

---

### Task 0：Spike——確認 hook payload（手動，需要使用者核准修改 settings）

**Files：**
- Create：`docs/changes/2026-11-04-hook-payload-spike.md`（記錄觀察結果）

- [ ] **Step 1**：commit 目前尚未提交的 spec、plan 和 research 檔，此時還沒有 gate：`git add docs && git commit -m "docs: workflow research, design spec and plan"`。
- [ ] **Step 2**：請使用者核准後，在 `~/.claude/settings.json` 暫時加入 `PostToolUse`、`PostToolUseFailure`，matcher 都設為 `Bash|PowerShell|Agent|Task`，指令把 stdin 附加到 `<home>/AppData/Local/Temp/hook-dump.jsonl`。
- [ ] **Step 3**：開一個新 session，依序執行 `python -c "pass"`（成功）、`python -c "import sys;sys.exit(3)"`（失敗）、PowerShell 的 `$env:CLAUDE_CODE_CHILD_SESSION`，再派一個 Agent。
- [ ] **Step 4**：把觀察結果寫進 spike 檔，包括：
  - 子代理工具實際的 `tool_name`
  - prompt 所在的欄位
  - `PostToolUseFailure.error` 第一行的格式
  - `cwd` 的格式
  - Bash 和 PowerShell 中 `CLAUDE_CODE_CHILD_SESSION` 是否都是 `1`

  若結果和下面各 task 的假設不同，就修改 Task 4、Task 6 的 Interfaces 再繼續。
- [ ] **Step 5**：移除暫時加入的 hook，commit spike 檔。

### Task 1：設定載入與檔案分類

**Files：** Create `tools/gate.py`、`tests/test_gate_classify.py`

**Interfaces：**
- Produces：
  - `git(repo: Path, *args: str, env: dict | None = None, check: bool = True) -> str`：帶上 Global Constraints 的 `-c` 參數，回傳 stdout。
  - `repo_root(cwd: Path) -> Path | None`
  - `load_config(repo: Path) -> dict | None`：沒有 `.agent-gate` 時回傳 `None`；回傳的鍵為 `test_commands: list[str]`、`sensitive: list[str]`、`architecture: str`。
  - `classify(path: str, cfg: dict) -> str`：回傳 `"doc" | "config" | "high" | "test" | "source"` 其中之一。

- [ ] **Step 1：寫失敗的測試**，至少要有以下 assert：
  ```python
  cfg = {"test_commands": [], "sensitive": ["**/auth/**"], "architecture": "docs/architecture/ARCHITECTURE.md"}
  assert classify("README.md", cfg) == "doc"
  assert classify("docs/x.py", cfg) == "doc"
  assert classify("conf/app.yaml", cfg) == "config"
  for p in [".github/workflows/ci.yml", "package.json", "pyproject.toml", "requirements-dev.txt",
            "Cargo.toml", "go.mod", "uv.lock", ".claude/settings.json", ".agent-gate", "src/auth/login.py"]:
      assert classify(p, cfg) == "high", p
  for p in ["tests/a.py", "src/__tests__/b.ts", "test_x.py", "x_test.go", "a.test.ts", "a.spec.ts", "spec/a.rb"]:
      assert classify(p, cfg) == "test", p
  assert classify("rea/bridge/pwndbg/inspect.py", cfg) == "source"
  assert classify("src/中文 檔.py", cfg) == "source"
  ```
  另外要測 `load_config`：沒有 `.agent-gate` 時回傳 `None`；有檔但沒寫 `architecture` 時，`architecture` 取預設值。
- [ ] **Step 2**：執行 `python -I tests/test_gate_classify.py`，預期失敗並出現 ImportError。
- [ ] **Step 3：實作**。分類的優先順序是 high（含 `sensitive`）> test > doc > config > source。
  - `sensitive` 用 `fnmatch` 比對。
  - test 依路徑段或檔名規則判斷。
  - `*.txt` 算 doc，但 `requirements*.txt` 已經先被 high 攔下。
  - lockfile 的清單：`*.lock`、`package-lock.json`、`pnpm-lock.yaml`、`yarn.lock`。
- [ ] **Step 4**：再跑一次，預期印出 `ok`。
- [ ] **Step 5**：commit。

### Task 2：front matter 與 change 檔解析

**Files：** Modify `tools/gate.py`；Create `tests/test_gate_frontmatter.py`

**Interfaces：**
- Produces：
  - `parse_front_matter(text: str) -> tuple[dict, str]`：支援 `key: value`、`key: [a, b]`、`key:` 後面接 `- item` 的寫法，以及 `#` 註解和帶引號的值。沒有 front matter 時回傳 `({}, text)`。
  - `section(body: str, heading_prefix: str) -> str`：回傳以 `## <heading_prefix>` 開頭的段落內文，已去除前後空白。

- [ ] **Step 1：寫失敗的測試**：
  - 把 spec 第 2 節的 change 檔範例換成 `\r\n` 換行後解析，預期得到：
    - `fm["tier"] == "T2"`、`fm["components"] == ["api", "auth"]`
    - `fm["verified_by"] == ["pytest tests/test_auth.py", "manual: localhost 登入成功"]`
    - `fm["supersedes"] == []`
  - `section(body, "決策")` 在「決策（含 Rulings）」標題底下沒有內容時，回傳 `""`。
- [ ] **Step 2**：跑測試，預期失敗。**Step 3**：實作。**Step 4**：跑測試，預期印出 `ok`。**Step 5**：commit。

### Task 3：commit-msg 的 Tier 與 Change 規則

**Files：** Modify `tools/gate.py`；Create `tests/test_gate_commitmsg.py`、`tests/gate_fixtures.py`（暫存 repo 的輔助函式）

**Interfaces：**
- Consumes：Task 1、Task 2 的函式。
- Produces：
  - `staged(repo: Path) -> list[tuple[str, str]]`：`(status, path)`，用 `diff --cached --name-status -M -z`；沒有 HEAD 時比對 empty tree。
  - `open_changes(repo: Path) -> list[str]`：index 裡 `status` 為 `proposed` 或 `partial` 的 `docs/changes/*.md`。
  - `check_commit(repo: Path, msg: str, cfg: dict) -> list[str]`：回傳錯誤字串清單，空清單代表放行。Task 5 的 `verify_done` 由這裡呼叫。
  - `tests/gate_fixtures.py`：`make_repo(files: dict[str, str], gate: str | None = DEFAULT_GATE) -> Path`，以及 `stage(repo, files: dict)`。

- [ ] **Step 1：寫失敗的測試**，每個情境 assert 錯誤清單是否為空，或包含指定的關鍵字：

  | 情境 | 預期 |
  |---|---|
  | 沒有 `Tier:` | 錯誤含 `Tier` |
  | `Tier: T0`，staged `src/a.py` | 錯誤含 `T2` |
  | `Tier: T0`，staged `.github/workflows/x.yml` | 錯誤 |
  | `Tier: T0`，`git mv a.py b.py`（R100） | 放行 |
  | `Tier: T1`，新增 `src/new.py` | 錯誤 |
  | `Tier: T1`，修改一個原始碼檔、新增一個測試檔 | 放行 |
  | `Tier: T1`，修改 `src/auth/x.py`（sensitive） | 錯誤 |
  | `Tier: T2`，沒有 `Change:` | 錯誤 |
  | `Change:` 指向不存在的檔 | 錯誤 |
  | change 檔的 `tier: T3` 但 trailer 寫 `T2` | 錯誤 |
  | `status: shipped` | 錯誤 |
  | index 裡有 `partial` change，`Tier: T1` 修改原始碼但沒有 `Change:` | 錯誤 |
  | 同上，但只改 `README.md` | 放行 |
  | 存在 `MERGE_HEAD` 而且有 `Tier:` | 放行 |
  | 第一個 commit（沒有 HEAD）、`Tier: T0`、只有 `README.md` | 放行 |
  | message 用 `\r\n` 換行 | 能解析出 trailer |
  | 修改中文檔名 `src/中 文.py` 且 `Tier: T1` | 放行 |

- [ ] **Step 2**：跑測試，預期失敗。
- [ ] **Step 3**：實作 `check_commit`。`status` 是 `done` 時呼叫 `verify_done`；在 Task 5 完成前，先做成一律回傳 `[]` 的 stub。
- [ ] **Step 4**：跑測試，預期印出 `ok`。**Step 5**：commit。

### Task 4：證據日誌

**Files：** Modify `tools/gate.py`；Create `tests/test_gate_evidence.py`

**Interfaces：**
- Produces：
  - `log_path(repo: Path) -> Path`：`<git-common-dir>/agent-evidence.jsonl`。
  - `tree_snapshot(repo: Path) -> str`：用暫存的 `GIT_INDEX_FILE`，先 `read-tree HEAD`（沒有 HEAD 就略過這步），再 `add -A`，最後 `write-tree`。
  - `handle_evidence(payload: dict, now: float) -> None`：依 payload 的事件類型和工具名稱寫入一筆紀錄，格式見 spec 3.4。測試指令以前綴比對 `test_commands`，比較前先把連續空白壓成一個。
  - `read_log(repo: Path) -> list[dict]`
  - `append_log(repo: Path, rec: dict) -> None`

- [ ] **Step 1：寫失敗的測試**：
  - 成功的 Bash payload，指令是 `pytest  -q`（兩個空格），`test_commands=["pytest"]` → 寫入一筆 `kind=test, ok=True`，`tree` 等於 `tree_snapshot`。
  - Failure payload → 寫入 `ok=False`。
  - 指令是 `ls` → 不寫入。
  - Agent payload 的 prompt 含 `docs/changes/2026-01-01-x.md` → 寫入 `kind=agent`，`prompt_paths` 等於 `["docs/changes/2026-01-01-x.md"]`。
  - 沒有 `.agent-gate` 的 repo → 不寫入。
  - 沒有 HEAD 的 repo，`tree_snapshot` 不能丟出例外。
  - 在 worktree 裡和在主 repo 裡，`log_path` 相同。
- [ ] **Step 2**：跑測試，預期失敗。**Step 3**：實作；欄位名稱以 Task 0 spike 的觀察結果為準。**Step 4**：跑測試，預期印出 `ok`。**Step 5**：commit。

### Task 5：done 時的完整驗證

**Files：** Modify `tools/gate.py`；Create `tests/test_gate_done.py`

**Interfaces：**
- Consumes：`staged`、`parse_front_matter`、`section`、`read_log`、`tree_snapshot`。
- Produces：
  - `change_base(repo: Path, change_path: str) -> str`：引進這份 change 檔的第一個 commit 的 parent。若 change 檔還沒進過 history，或那個 commit 是 root commit，就回傳 HEAD 或 empty tree。
  - `architecture_ids(text: str) -> set[str]`：取出 ARCHITECTURE.md 中 `## AI structured data` 那段 YAML 的所有 `- id: x`。
  - `hunks(repo: Path, base: str) -> dict[str, list[tuple[int, int]]]`：用 `diff --cached -U0 <base>`，記錄新檔案那一側的行號區間。
  - `verify_done(repo: Path, change_path: str, fm: dict, body: str, cfg: dict, tier: str, now: float) -> list[str]`

- [ ] **Step 1：寫失敗的測試**。先準備一個 fixture repo：含 ARCHITECTURE.md（ids：`api`）、`.agent-gate`（`test_commands=["python -I tests"]`），和一份從 `partial` 改成 `done` 的 change 檔。

  | 情境 | 預期 |
  |---|---|
  | `components: [nope]` | 錯誤 |
  | 「行為改變」段有內容，但本變更範圍內沒動過 ARCHITECTURE.md | 錯誤 |
  | 同上，「行為改變」段是空的 | 不因為這條出錯 |
  | `evidence: [src/a.py:999]` | 錯誤 |
  | `evidence` 指向 hunk 內的行 | 放行 |
  | `verified_by` 沒有任何一條符合 `test_commands` | 錯誤 |
  | 有成功的測試紀錄，但之後 `src/a.py` 又改過再 stage | 錯誤 |
  | 有成功的測試紀錄，tree 和 index 一致 | 放行 |
  | 只有 `manual:` 的 `verified_by` | 錯誤（仍然需要一條測試指令） |
  | 沒有提到這份 change 路徑的 agent 紀錄 | 錯誤 |
  | T3 的「決策」段是空的 | 錯誤 |
  | Review Focus 5：成功紀錄（tree 一致）之後又有一筆失敗紀錄 | 放行，用這個測試把行為釘住 |

- [ ] **Step 2**：跑測試，預期失敗。
- [ ] **Step 3：實作**。blob 比對：對本變更 diff 中的每個路徑，比較 `git rev-parse :<path>` 和 `git rev-parse <tree>:<path>`；兩邊都不存在也算一致。agent 紀錄要在 `change_base` 那個 commit 的時間之後；若 change 檔尚未進過 history，則不限時間。
- [ ] **Step 4**：跑測試，預期印出 `ok`。**Step 5**：commit。

### Task 6：pretool 子指令

**Files：** Modify `tools/gate.py`；Create `tests/test_gate_pretool.py`

**Interfaces：**
- Produces：
  - `check_pretool(command: str) -> str | None`：回傳擋下的理由，`None` 代表放行。
  - `retro_warning(repo: Path) -> str | None`：列出 `.agent-gate` 加入之後所有缺 `Tier:` 的 commit，排除 `<git-dir>/gate-ack` 裡已確認的 hash。
  - `handle_pretool(payload: dict) -> tuple[int, str]`：回傳 exit code 和輸出。擋下時是 exit 2 加 stderr；只有警告時是 exit 0，stdout 輸出 `{"systemMessage": ...}`。

- [ ] **Step 1：寫失敗的測試**：
  - **要擋下**：
    - `git commit --no-verify -m x`
    - `git commit -nm x`
    - `git -c core.hooksPath=/dev/null commit -m x`
    - `unset CLAUDE_CODE_CHILD_SESSION; git commit -m x`
    - `env -u CLAUDE_CODE_CHILD_SESSION git commit`
    - `$env:CLAUDE_CODE_CHILD_SESSION=''; git commit`
    - `git cherry-pick abc`
    - `git revert HEAD`
    - `git rebase main`
    - `git am x.patch`
    - `git commit-tree t`
    - `git update-ref refs/heads/x y`
  - **要放行**：
    - `git log --grep commit`
    - `git show HEAD`
    - `git commit -m "fix -n flag parsing"`：`-n` 出現在引號內不算
    - `ls -n`
  - `retro_warning`：fixture 中有一個缺 trailer 的 commit 時，回傳的字串包含它的短 hash；把它寫進 gate-ack 之後回傳 `None`。
  - 沒有 `.agent-gate` 的 repo：`handle_pretool` 回傳 `(0, "")`。
- [ ] **Step 2**：跑測試，預期失敗。
- [ ] **Step 3：實作**：先用 `shlex.split(posix=True)` 拆 token，拆不了時退回用空白切；再對 token 序列做比對。
- [ ] **Step 4**：跑測試，預期印出 `ok`。**Step 5**：commit。

### Task 7：install 與 CLI 入口

**Files：** Modify `tools/gate.py`；Create `tests/test_gate_cli.py`

**Interfaces：**
- Produces：
  - `main(argv: list[str]) -> int`
  - `install(repo: Path, gate_path: str) -> str`：回傳要給使用者看的訊息。
  - 子指令的行為：
    - `commit-msg <file>`：人類環境、沒有 `.agent-gate`、或錯誤清單為空時 exit 0，否則 exit 1。擋下或放行都 `append_log` 一筆 `kind=gate` 紀錄。
    - `pretool`、`evidence`：從 stdin 讀 JSON。
    - `install`：在 `cwd` 的 repo 安裝 hook。

- [ ] **Step 1：寫失敗的測試**：
  - `install` 會寫出 `.git/hooks/commit-msg`；內容含絕對路徑的 python 和 gate.py；在 POSIX 下有執行權限。
  - 原本就有 hook 時，舊的改名為 `commit-msg.local`，新的 hook 會先執行它，它失敗時整體也失敗。
  - repo 設了本地 `core.hooksPath` 時拒絕安裝。
  - 端到端情境（用 subprocess 跑真的 `git commit`）：

    | 情境 | 預期 |
    |---|---|
    | 環境變數 `CLAUDE_CODE_CHILD_SESSION=1`、沒有 `Tier:` | commit 失敗，stderr 第一行是 `gate: blocked (see skill change-record)` |
    | 不帶該環境變數 | commit 成功 |
    | `git commit -a -m "...Tier: T1"` 修改一個原始碼檔 | 成功，證明 `GIT_INDEX_FILE` 路徑可用 |
- [ ] **Step 2**：跑測試，預期失敗。**Step 3**：實作。**Step 4**：跑測試，預期印出 `ok`。**Step 5**：commit。

### Task 8：skill 改動

**Files：**
- Create `skills/change-record/SKILL.md`
- Modify `skills/c4-architecture/SKILL.md`（YAML 範例和 Rules 段）
- Modify `skills/git-workflow-and-versioning/SKILL.md`（「Descriptive Messages」段之後、「Change Summaries」段）

- [ ] **Step 1**：寫 `change-record`：
  - frontmatter：`name: change-record`，description 以「Use when writing or updating a docs/changes file, when a commit is blocked by the tier gate, or when setting up .agent-gate」開頭。
  - 內文依序放：
    - change 檔模板（照抄 spec 第 2 節）
    - 欄位說明
    - `.agent-gate` 格式
    - gate 規則摘要（spec 3.2 的 1–5）
    - reviewer 每條結論都要附 `path:line` 或指令
    - 被擋下時只能補齊或問人
    - 「待人工確認」的格式
  - 篇幅控制在 120 行以內。
- [ ] **Step 2**：c4 的改動：YAML 範例的元素加上 `behavior: [Rejects orders without stock]`；Rules 加兩條：
  - 「`behavior` lists what the element guarantees now; update it when a change alters behavior」
  - 「Existing projects may list only the elements a change touches」
- [ ] **Step 3**：git-workflow 加一小段「Tier and Change trailers」，內容是兩個 trailer 的格式和範例，以及 PR 說明的第一段只高亮 `manual:`、`reviewed_by` 和 retro 警告。
- [ ] **Step 4**：執行 `python -I tools/skill_audit.py local=skills`，預期這三個 skill 都沒有任何 flag。
- [ ] **Step 5**：commit。

### Task 9：CLAUDE.md 草稿與 routing eval

**Files：** Modify `CLAUDE.md.draft`、`evals/routing.json`

- [ ] **Step 1**：用 spec 第 1 節的表格取代 `CLAUDE.md.draft` 第 1–3 條，表格最多 15 行，再加三行：
  - 「被 gate 擋下時只能補齊或停下來問人；不得繞過、降級 Tier 或修改 gate 相關檔案」
  - 「T3 的 spec 和 plan 寫在 `docs/changes/`」
  - 「T2/T3 收尾時在最後列出『待人工確認』」

  原本的第 4–8 條和「環境」段保留。改完後檔案總行數要少於 45 行。
- [ ] **Step 2**：`routing.json` 新增 area 為 `tier` 的 20 個 case：T0–T3 各 5 個，每個都有 `prompt` 和 `expected`（預期級別，以及是否觸發 brainstorming），`observed_baseline` 留空。`_note` 補上「每題 5 runs」。
- [ ] **Step 3**：用 `python -I -c "import json;json.load(open('evals/routing.json',encoding='utf-8'))"` 確認 JSON 有效。
- [ ] **Step 4**：commit。

### Task 10：部署與試用（需要使用者核准修改 settings）

**Files：** Create `.agent-gate`、`AGENTS.md`；Modify `~/.claude/settings.json`、`~/.claude/CLAUDE.md`

- [ ] **Step 1**：跑全部測試，每支都要印出 `ok`：`for f in tests/test_gate_*.py tests/test_skill_audit.py; do python -I "$f"; done`。
- [ ] **Step 2**：部署：
  - 複製 `tools/gate.py` 到 `<home>/.claude/hooks/gate.py`。
  - 複製 `skills/change-record`、`c4-architecture`、`git-workflow-and-versioning` 到 `~/.claude/skills/`。
  - 把 `CLAUDE.md.draft` 去掉開頭的註解後，寫入 `~/.claude/CLAUDE.md`。
- [ ] **Step 3**：在 skill-lab 建立 `.agent-gate`（`test_commands = ["python -I tests/"]`）和 `AGENTS.md`（說明測試指令、change 檔位置，並連到 change-record），再執行 `python -I <home>/.claude/hooks/gate.py install`。這一步必須在 Step 4 之前完成，因為 deny 規則生效後，Claude 就不能再寫 `.agent-gate`。
- [ ] **Step 4**：把 settings.json 的完整 diff 給使用者核准，再寫入：
  - `PreToolUse`（`Bash|PowerShell`）→ `gate.py pretool`
  - `PostToolUse` 和 `PostToolUseFailure`（`Bash|PowerShell|<spike 確認的 Agent 工具名>`）→ `gate.py evidence`
  - `ConfigChange`（`user_settings`）→ exit 2
  - spec 3.5 的 `permissions.deny` 清單
- [ ] **Step 5**：在新 session 用一個真的 T2 小變更走完整條流程，例如替 `skill_audit.py` 加 `--json` 輸出。確認以下四點：缺 trailer 時被擋下；`done` 時通過；使用者自己在終端機 commit 時放行；`--no-verify` 被 pretool 擋下。
- [ ] **Step 6**：把這個變更的 change 檔設成 `done` 並 commit。這個 commit 本身就是第一次正式通過 gate 的驗收。之後開始為期兩週的擋下紀錄觀察。
