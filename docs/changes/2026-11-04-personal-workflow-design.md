---
tier: T3
status: done
components: []          # skill-lab 尚無 ARCHITECTURE.md；試用階段補上
evidence: []
verified_by: []
reviewed_by: []
supersedes: []
---
# 自用 agentic coding 工作流設計（方案 A：薄路由層）

- 研究依據：[docs/research/2026-11-04-agentic-workflows/](../research/2026-11-04-agentic-workflows/README.md)
- 修訂紀錄：
  - r1 是初稿。
  - r2（同日）依外部審查意見書修訂，並補上我自己查到的五個問題：`CLAUDECODE` 在 IDE 終端機也會設定、全域 `hooksPath` 會蓋掉 repo 原有的 hook、cherry-pick／revert／rebase 不會觸發 hook、`ConfigChange` 只作用於當下 session、改用 git hook 後 `--no-verify` 又能繞過。這五點的說明見「決策」段。

## 為什麼

使用者目前的工具有 superpowers、ponytail、skill-lab 個人 skill 和 CLAUDE.md，有三個痛點：

1. **skill 互相打架**：四層都在下流程指令。
2. **產出難以交接**：spec、計畫、決策散落各處，別人或新 session 的 AI 接不起來。
3. **品質不穩**：七套主流工作流的品質關卡幾乎都只寫在 prompt 裡，AI 可以不理會。

使用條件：個人為主、偶爾協作；新舊專案各半；成本依風險分級；程式強制只放在收尾。只在 Windows 上的 Claude Code 使用，不做跨模型家族審查。

方案 A：superpowers 和 ponytail 原樣保留，在上面加一層薄的路由與收尾檢查。不選 B（fork superpowers）是因為它兩個月出四版，自己維護的成本太高。不選 C（OpenSpec CLI）是因為會多一個依賴和一套概念。

## 1. 風險分級與路由

分級表寫在 `~/.claude/CLAUDE.md`，取代現行第 1–3 條，**控制在約 15 行**。gate 的細節不放這裡，放在 change-record skill，被擋下時錯誤訊息會指向它。

| 級 | 判斷條件 | 流程 | 審查 |
|---|---|---|---|
| T0 瑣碎 | 只動文件或低風險設定，或純改名 | 直接改 | 自審 |
| T1 小修 | 最多改一個既有的非測試原始碼檔、不新增原始碼檔、不改對外行為 | bug 修復先寫會失敗的測試 | 自審 |
| T2 功能 | 新行為、多檔改動，或碰到高風險設定或敏感路徑 | brainstorming 的 bounded 路徑 → TDD | fresh-context reviewer，只給 diff 和需求，不附作者結論；每條結論都要附上 `path:line` 或實際跑過的指令 |
| T3 架構 | 新專案或子系統、改公開介面、需要重組結構 | brainstorming 全流程 → spec（寫在 `docs/changes/`）→ writing-plans → 子代理逐任務執行 → final review | 每個 task 一次，再加整支 branch 一次 |

- bug 修復依改動範圍分級，不一律算 T1。
- 只能往上升級，不能往下降級。
- 每次回覆第一行標出級別。
- T2/T3 收尾時，回覆最後一段列出「待人工確認」。
- ponytail 只管程式寫法。它注入的流程規則（例如新邏輯要附測試）和分級表重疊，有衝突時依 CLAUDE.md 第 5 條處理。重疊程度用第 5 節的 routing eval 量測，不靠推理判斷。

## 2. 交接檔

| 檔案 | 回答什麼問題 | 性質 |
|---|---|---|
| `AGENTS.md` | 怎麼建置、怎麼測試、其他檔放在哪；連到 change-record skill | 給人和其他 AI 讀，**不當作 gate 開關** |
| `.agent-gate`（TOML） | gate 開關，同時存放機器設定：測試指令前綴、敏感路徑 glob | 有這個檔才啟用 gate |
| `ARCHITECTURE.md` + `docs/adr/` | 現在的結構、每個元件保證什麼行為（`behavior:`）、為什麼這樣設計 | 現況快照；舊專案可以只寫動到的元件 |
| `docs/changes/YYYY-MM-DD-<slug>.md` | 一個**變更**（不是一個 commit）改了什麼、為什麼、怎麼驗證 | 歷史；變成 `done` 之後就不再修改 |

`.agent-gate` 範例：

```toml
test_commands = ["pytest", "uv run --isolated --no-project --python 3.13 pytest"]  # 以前綴比對
sensitive     = ["**/auth/**", "**/payments/**", "migrations/**"]                  # 碰到就至少算 T2
```

change 檔格式：

```markdown
---
tier: T2                     # T2 | T3
status: partial              # proposed | partial | done | abandoned
components: [api, auth]      # ARCHITECTURE.md 的元件 id
evidence: [src/auth.py:42]   # path:line，必須落在本變更 diff 的 hunk 內
verified_by:
  - pytest tests/test_auth.py          # 至少一條必須符合 .agent-gate 的 test_commands
  - "manual: localhost 登入成功"        # 機器無法驗證，會被高亮
reviewed_by: [fresh-context subagent]
supersedes: []
---
## 為什麼
## 行為改變
## 決策（含 Rulings）
## 沒做／已知限制
```

- superpowers SDD 收尾時會刪掉 ledger，刪之前要先把裡面的 Rulings 抄進「決策」段。

## 3. 收尾檢查（gate）

整個 gate 分三個部分，都在 repo 有 `.agent-gate` 時才作用：

1. **git `commit-msg` hook**：主要的檢查，3.2 的規則都在這裡執行。
2. **薄的 Claude Code `PreToolUse` hook**：擋下會繞過 git hook 的指令。
3. **證據日誌**：記錄測試跑過的內容和 reviewer 派發。

### 3.1 git hook：安裝與辨識 Claude

- 要啟用 gate 的 repo，執行 `python gate.py install`：
  - 只寫入該 repo 的 `.git/hooks/commit-msg`。如果原本已經有 hook，就改名成 `commit-msg.local`，由新的 hook 先呼叫它。
  - **不使用全域 `core.hooksPath`**：實測確認，設了全域 `core.hooksPath` 之後，git 會忽略每個 repo 自己的 `.git/hooks`。
  - repo 本身設定了本地 `core.hooksPath`（例如用 husky）時，install 會拒絕並說明原因，由使用者手動處理。
- **辨識是不是 Claude 在 commit**：只有環境變數 `CLAUDE_CODE_CHILD_SESSION=1` 時才檢查，否則一律放行。
  - 官方文件說這個變數只由 Claude Code 的 Bash、PowerShell 工具和 hook 子程序設定。
  - 不用 `CLAUDECODE`：它在 IDE 內建終端機也會被設成 1，會把使用者自己 commit 的出口一起擋掉。
- 只用 `commit-msg` 一個 hook，因為它同時拿得到兩樣東西：
  - 最終的 commit message 檔。
  - 實際要 commit 的 index：`commit -a` 時，git 會設定 `GIT_INDEX_FILE`。
- 它由 `git commit` 和 `git merge` 觸發，所以舊版「commit 必須單獨一條指令」和指令字串解析都刪除了。
- hook 指令一律寫絕對路徑：`C:/Python313/python.exe -I <home>/.claude/hooks/gate.py commit-msg "$1"`。

### 3.2 commit-msg 的檢查規則

1. **檔案分類**：
   - 用路徑段比對，不用子字串，所以 `inspect.py` 不會被當成測試。
   - 分類如下：

     | 類別 | 範圍 |
     |---|---|
     | 文件 | `*.md`、`*.txt`、`docs/` |
     | 低風險設定 | 其餘的 `json`／`yaml`／`toml`／`ini` |
     | 高風險 | `.github/`（整個目錄）、`.gitlab-ci.yml`、`.circleci/`、依賴清單（`package.json`、`pyproject.toml`、`requirements*.txt`、`Cargo.toml`、`go.mod`、lockfile）、`.claude/`、`.agent-gate`，以及 `.agent-gate` 的 `sensitive` |
     | 測試 | 路徑段為 `test`、`tests`、`__tests__`、`spec`，或檔名符合 `test_*`、`*_test.*`、`*.test.*`、`*.spec.*` |
     | 原始碼 | 其餘所有檔案 |

2. **Tier trailer**：必須有 `Tier: T0`–`T3`。
   - T0：只能有文件、低風險設定，或純改名（R100）。
   - T1：最多一個**修改的**非測試原始碼檔，不能新增原始碼檔，不能碰高風險。
   - 不符合就擋下，並提示「看起來是 T2」。
3. **Change trailer**：
   - T2/T3 必須帶 `Change: docs/changes/<file>.md`，而且那個檔要存在於 index。
   - 如果 index 裡有任何 `status` 為 `proposed` 或 `partial` 的 change 檔，**所有動到原始碼的 commit 都必須帶 `Change:`**，不論 Tier。這是為了堵住「T3 功能的各個 task 都標成 T1 溜過去」的漏洞。
   - 同一個變更的多個 commit 引用同一份 change 檔，不必每次新增。
4. **每次都檢查**：front matter 的 `tier` 和 trailer 一致，`status` 是合法值。
5. **只在 `status` 變成 `done` 的那個 commit 做完整驗證**。「本變更」指的是從 change 檔第一次出現的 commit 的 parent，到目前 index 為止的累積 diff。
   - `components` 不能為空，每個 id 都要在 `ARCHITECTURE.md` 的 YAML 中找得到。
   - 「行為改變」段不是空的時，本變更範圍內必須動過 `ARCHITECTURE.md`。這是防碎片化和避免無意義修改之間的折衷：沒有行為改變時，把 `## 行為改變` 留空（空標題仍留在檔案裡，人一看就知道）。
   - `evidence` 的每個 `path:line` 都要落在本變更 `-U0` diff 的 hunk 範圍內。
   - `verified_by` 至少一條要符合 `test_commands`，而且證據日誌裡最後一次**成功**的測試紀錄要和現在一致：本變更動到的每個路徑，在該次紀錄的 tree 中的 blob 都等於現在 index 的 blob。也就是說，**測試跑的正是要 commit 的內容**。
   - `reviewed_by` 不能為空，而且證據日誌裡在本變更開始之後，要有一筆 Agent 派發紀錄，其 prompt 提到這份 change 檔的路徑。
   - T3 另外要求「決策」段不能是空的。
6. 擋下時以非 0 結束，在 stderr 寫明缺什麼，並指向 change-record skill。

### 3.3 薄 PreToolUse hook（`Bash|PowerShell`）

只在有 `.agent-gate` 的 repo 生效，只擋會繞過 git hook 的指令，這幾種寫法都直接擋下：

- `--no-verify`，或 `commit`／`merge` 時的 `-n`
- `core.hooksPath`
- 修改或刪除 `CLAUDE_CODE_CHILD_SESSION` 的指令（`unset`、`env -u`、重新指定值）
- `git cherry-pick`、`git revert`、`git rebase`、`git am`、`git commit-tree`、`git update-ref`。實測確認前三個不會觸發 commit-msg hook，所以這幾個請使用者自己執行。

**事後追查**也放在這裡，因為只有 Claude Code hook 能用 `systemMessage` 直接告訴使用者：

- Claude 下 `git commit` 或 `git merge` 時，掃描 `.agent-gate` 加入之後所有缺 `Tier:` 的 commit。
- 找到就警告使用者，但不擋 commit。
- 使用者把 hash 寫進 `.git/gate-ack` 就不再提醒。

### 3.4 證據日誌

位置是 `$(git rev-parse --git-common-dir)/agent-evidence.jsonl`。用 common dir 是為了讓 worktree 共用同一份日誌，而且不進版控。

| 事件 | 條件 | 記錄 |
|---|---|---|
| `PostToolUse`（`Bash\|PowerShell`） | 指令符合 `test_commands` 前綴 | `{"t","kind":"test","ok":true,"cmd","tree"}` |
| `PostToolUseFailure`（同上） | 同上 | `ok:false` |
| `PostToolUse`（Agent 工具） | 每次派發 | `{"t","kind":"agent","agent_type","prompt_paths"}`，`prompt_paths` 是 prompt 中出現的 `docs/changes/*.md` 路徑 |
| gate 自己 | 每次擋下或放行 | `{"t","kind":"gate","decision","reason"}`，用於第 5 節的量測 |

- `tree` 的算法：用暫存 index 執行 `git add -A` 再 `git write-tree`，得到當時整個工作區的 tree id（會遵守 `.gitignore`）。
- 不再記錄 edit 事件，也不依賴 `bashEditDiff`。官方文件明說它「not to enforce a policy」，而且預設只在 auto 和 bypass 模式下記錄。
- 實作的第一步：用一個先把 stdin 存檔的 hook，確認本機實際收到的 payload，包括 Agent 工具的名稱和 prompt 欄位、`PostToolUseFailure` 的 `error` 格式。

### 3.5 防止繞過

- `permissions.deny`：禁止用 Edit/Write 修改 `<home>/.claude/hooks/**`、`<home>/.claude/settings.json`、`**/.git/hooks/**`、`**/.git/agent-evidence.jsonl`、`**/.git/gate-ack`、`**/.agent-gate`。
- `ConfigChange` hook 擋下 `user_settings` 在 session 中途生效。這只是補強：檔案在磁碟上還是會被改掉，下個 session 就會生效；而且擋下時不會有任何訊息，連使用者自己在 session 中途改設定也會被擋。
- CLAUDE.md 規定：被擋下時只能補齊缺的東西或停下來問人。不得改寫指令來繞過、不得降級 Tier、不得修改 gate 相關的檔案。
- 唯一合法的出口是使用者自己在終端機 commit。那個環境沒有 `CLAUDE_CODE_CHILD_SESSION`，所以 gate 會放行。

### 3.6 讓人看見「機器驗證不了」的部分

- T2/T3 收尾回覆和 PR 說明的第一段，只高亮以下項目：所有 `manual:` 項目、`reviewed_by`，以及 3.3 的事後追查警告。
- 不使用 CI。

## 4. 要改的檔案

skill-lab 原始檔改完後部署到 `~/.claude/`（CLAUDE.md 第 8 條）。

| 檔案 | 改動 |
|---|---|
| `CLAUDE.md.draft` → `~/.claude/CLAUDE.md` | 第 1–3 條換成約 15 行的分級表，再加「禁止繞過」「T3 spec 寫在 docs/changes/」「待人工確認」三行 |
| `skills/c4-architecture/` | YAML 加 `behavior:`；允許只寫動到的元件 |
| `skills/git-workflow-and-versioning/` | `Tier:`、`Change:` trailer；PR 說明的第一段 |
| `skills/change-record/`（新，model-invoked） | change 檔模板、gate 規則、`.agent-gate` 格式、reviewer 證據要求 |
| `tools/gate.py`（新） | 子指令：`install`、`commit-msg`、`pretool`、`evidence`。只用 Python 標準函式庫，TOML 用 `tomllib` 讀，front matter 用內建的極簡 parser |
| `~/.claude/settings.json` | PreToolUse、PostToolUse、PostToolUseFailure、ConfigChange 四個 hook，以及 deny 規則（使用者核准後才寫入） |
| skill-lab 的 `.agent-gate`、`AGENTS.md`（新） | 先在 skill-lab 自己身上試用 |

## 5. 測試與量測

- **gate 是確定性程式，正確性靠單元測試**。`tests/test_gate.py` 用暫存 git repo 跑以下情境，每個都要驗證是擋下還是放行：
  - 人類環境（沒有 `CLAUDE_CODE_CHILD_SESSION`）放行
  - 沒有 trailer
  - T0 夾帶原始碼
  - T0 夾帶 `.github/` 或 `package.json`
  - T1 新增檔案
  - `inspect.py` 不被當成測試
  - 碰到敏感路徑
  - 有 open change 時缺少 `Change:`
  - tier 不一致
  - `done` 時 component 不存在
  - 行號不在 hunk 內
  - 測試沒跑過、跑失敗、測完之後內容又改過
  - `manual:` 放行
  - reviewer 沒有派發紀錄
  - `commit -a` 時使用 `GIT_INDEX_FILE`
  - merge commit
  - 原本就有 hook 時會串接
  - `pretool` 擋下各種繞過寫法
  - 事後追查的警告
- **依賴模型的部分才需要重複量測**：
  - 擴充既有的 `evals/routing.json`，T0–T3 各 5 題，每題跑 5 次，統計分級是否正確、brainstorming 有沒有被誤觸發。
  - 試用兩週，從證據日誌的 gate 紀錄統計擋下率和誤擋率，再決定要不要推廣到其他 repo。

## 決策（Rulings）

- **路由寫在 CLAUDE.md**：compaction 之後 CLAUDE.md 會被重新讀取，skill 沒有這個保證。
- **不設字數門檻**：LLM 灌水沒有成本，字數也是可以被刷的指標。改用可以反查的欄位，再加內容 hash 證據。
- **主要檢查用 git `commit-msg` hook，不用 PreToolUse 的指令字串比對**：它拿得到最終 message 和 index，`merge` 也會觸發。代價是 `--no-verify` 可以繞過，所以由 3.3 的薄規則補上。
- **逐 repo 安裝，不設全域 `core.hooksPath`**：實測確認全域設定會讓 repo 原有的 hook 失效。
- **用 `CLAUDE_CODE_CHILD_SESSION` 辨識 Claude，不用 `CLAUDECODE`**：後者在 IDE 終端機也會被設定。
- **只在 `done` 時做完整驗證**，配合 `Change:` trailer：一個變更通常橫跨多個 commit，每個 commit 都要求完整交接檔，會把 commit 推大，也會讓交接檔碎片化。
- **證據用內容比對，不用時間順序**：`bashEditDiff` 官方明說不能用來強制，IDE 裡的手動編輯也不會被記錄。
- **保留「行為改變就要動 ARCHITECTURE.md」，但加條件**：外部審查建議刪掉，但這條是使用者為了防碎片化選的，所以折衷成只在「行為改變」段不是空的時才要求。
- **不加重複執行 gate 的驗收**：gate 是確定性程式，重複量測只用在依賴模型的部分。

## 沒做／已知限制

- **Predates the gate**: written before .agent-gate existed, so it was never gate-verified.
- **A later failing test run after a successful one is ignored**: the gate accepts any successful run that tested exactly the committed content.
- **用 Bash 偽造證據日誌**：deny 規則只擋 Edit/Write，擋不住 Bash 寫檔。除了 CLAUDE.md 的規定，沒有更強的防護。
- **間接繞過**：例如寫成腳本執行、GitPython、Bash 的 alias。當下擋不住，只能靠 3.3 的事後追查警告。
- **能證明跑過，不能證明有意義**：證據日誌能證明「測試跑的就是這份內容，而且通過」，不能證明測試測到了該測的東西。reviewer 派發紀錄也只能證明「有派」，不能證明「審得好」。
- **同一模型的 reviewer 有共同盲點**：fresh context 去不掉這點，最後一道關卡仍然是「待人工確認」清單。
- **不做的事**：累積式 `specs/`、TSV 決策日誌、CI、跨模型家族審查、全域 git hook。
