# Spec-driven agentic coding 三套工作流原始碼研究：BMAD-METHOD、OpenSpec、Spec Kit

研究日期：2026-11-04。方法：`git clone --depth 1` 三個 repo（BMAD 另 clone `V6.12` 分支），閱讀 agent/skill 檔、模板、schema、CLI 原始碼；並查 npm/PyPI registry 與 GitHub Blog。未執行任何 repo 內的腳本或安裝器。

Clone 位置（下文路徑皆相對於此）：`<redacted>/scratchpad/src/`
- `BMAD-METHOD/`：main，commit `022be93`（2026-11-02），v7 preview alpha
- `bmad-v6/`：`V6.12` 分支（2026-10-14），即 npm stable 6.12.4
- `OpenSpec/`：main，commit `2bd5bc3`（2026-11-02），package 1.16.0
- `spec-kit/`：main，commit `a227e38`（2026-11-03），`1.3.1.dev0`（剛發布 1.3.0）

---

## 0. 先講最重要的發現

1. **BMAD 跟大多數第三方報告描述的已經不是同一個東西。** 第三方文章通常描述 v4 到 v6 早期的「Analyst → PM → Architect → SM → Dev → QA 多角色接力」。到了 v6.3.0（2026-04），Bob (SM)、Quinn (QA)、Barry 都已經併進 Amelia (Dev)。v6.11.0（2026-08）把 `bmad-check-implementation-readiness` 刪掉，改成 `bmad-sprint-planning` 開頭的一道 readiness gate。v7（main 分支，預計 2026-11 中旬發布）又拿掉 sprint-planning，改由新的 Sofia（Product Owner）加上 `tickets.py` 管理 ticket tree。
2. **三者的 gate 幾乎都是 prompt，不是程式。** 真正由程式強制的只有以下幾項：
   - OpenSpec：`openspec validate` 與 `archive` 的結構驗證、未完成 task 的阻擋。
   - Spec Kit：`check-prerequisites` 腳本檢查檔案是否存在；`specify workflow run` 的 `type: gate` 人工核准步驟。
   - BMAD：`sprint_plan.py` 與 `tickets.py` 做結構和相依檢查（循環、drift）；「能不能實作」的判斷仍交給 LLM。
3. **Spec Kit 不是「專為 regulated 環境設計」。** 這是報告自己加上的詮釋。官方只說可以用 preset 來「Enforce organizational or regulatory standards」。constitution 與 governance 是真的有，但「full traceability audit」找不到。

---

## 1. BMAD-METHOD

### 1.1 版本線

| 線 | 版本 | 日期 | 安裝 |
|---|---|---|---|
| Stable | v6.12.4 | 2026-10-14（npm `latest`） | `npx bmad-method install` |
| Preview | v7 alpha（main） | 持續變動，README 寫「v7 release ETA is mid-November 2026」 | `npx skills add bmad-code-org/BMAD-METHOD --skill '*'` 或 Claude Code / Codex plugin marketplace |

### 1.2 驅動方式

- **全部是 skill（`SKILL.md`）。** 舊版的 agent YAML、web bundles、`.bmad-core/` 都已移除（v7 changelog：「Web bundles are removed」）。
- **Persona 是一種「有選單的 skill」。** 例如 `skills/bmad-agent-analyst/SKILL.md`：啟動時先執行 `uv run _bmad/scripts/resolve_customization.py` 合併三層 TOML（skill 預設 → `_bmad/custom/{skill}.toml` → `.user.toml`），接著「Adopt Persona」，然後顯示選單代碼（例如 PM 的 `PRD`、`IR`、`CC`），停下來等使用者輸入。
- **v7 的 workflow skill 走 render 機制**（`skills/bmad-build/SKILL.md`）。skill 本身只叫 agent 執行 `uv run _bmad/scripts/render_skill.py`，由腳本把 Jinja 化的 workflow 和使用者設定渲染成內容定址的不可變快照，放在 `_bmad/render/`，並附 `manifest.json`。agent 照輸出走；腳本印出 `HALT:` 就停。這讓「實際執行的 prompt」可檢視、可重現，是 v6.11 起的重大設計。
- **人設清單**（v6.12 / v7）：

| Persona | Skill | 職責 |
|---|---|---|
| Mary | `bmad-agent-analyst` | 研究、brief、PRFAQ、project context |
| John | `bmad-agent-pm` | PRD、epics/stories、readiness（v6） |
| Winston | `bmad-agent-architect` | architecture spine、readiness（v6） |
| Sally | `bmad-agent-ux-designer` | UX |
| Amelia | `bmad-agent-dev` | Build、QA、code review、sprint、retro |
| Sofia | `bmad-agent-po`（僅 v7） | 取代 `bmad-spec`、`bmad-ticket`、`bmad-correct-course` |
| Paige | Tech Writer | v6.11 退役 |
| Bob（SM）、Quinn（QA）、Barry | — | v6.3.0 併入 Amelia |

### 1.3 階段與產出

**v6.12（stable）**，Phase 4 為 `bmad-sprint-planning → bmad-build → bmad-code-review`。
- 規劃：`bmad-product-brief`、`bmad-prfaq`、`bmad-prd`（create/update/validate）、`bmad-ux`、`bmad-architecture`、`bmad-create-epics-and-stories`。
- 進入實作前：`bmad-sprint-planning` 先跑 readiness gate，再生成 `sprint-status.yaml`。

**v7（main）** 以「intent 是否 well-defined」決定路徑（`docs/plan/choose-a-planning-path.md`）。
- 模糊 intent：先用 `bmad-brainstorming`、`bmad-forge-idea`、`bmad-deep-recon`、`bmad-prfaq` 釐清。
- 清楚 intent：交給 Sofia 寫 requirements，再 slice 成 epic 與 story，寫進 `tickets.toml`。
- 每個 story 跑一次 `bmad-build`，epic 結束跑 `bmad-retrospective`。
- 產出路徑：`_bmad-output/initiative-<slug>/<type>-<slug>/<type>-<slug>.md`，epic 底下有 `tickets/` 子資料夾；`bmad-architecture` 產出 `architecture-<slug>.md`（「spine」，每個 AD 帶 Binds/Prevents/Rule）；UX 產出 `DESIGN.md` 與 `EXPERIENCE.md`；還有 `.memlog.md` 決策日誌。

**`bmad-build` 的 5 個 step 檔**（`step-01-clarify-and-route` … `step-05-present`，另有 `step-oneshot`）：
1. 先調查程式碼（深度搜尋交給 subagent），寫出 plan 檔的 `## Code Map`。
2. **CHECKPOINT 1**：HALT，讓使用者選 Approve and continue / Approve and stop / Review plan。核准後 `<frozen-after-approval>` 區塊鎖定，「only the human can change it」。
3. 實作交給 subagent，handoff recipe 可透過設定改由其他模型或外部 CLI 執行。
4. Review：多個 lens 並行（blind、edge-case-hunter、verification-gap，v6.11 起 Build Auto 另有 Intent Alignment Auditor），再做 triage，分類為 `intent_gap`、`bad_plan`、`patch`、`defer`。前兩類觸發 loopback，`review_loop_iteration > 5` 就 HALT。
5. 若 plan 帶有 I/O & Edge-Case Matrix，逐列確認有對應測試「實際有跑且通過」。

### 1.4 Gate：程式還是 prompt？

| Gate | 位置 | 強制方式 |
|---|---|---|
| Readiness gate（PASS/CONCERNS/FAIL） | `bmad-v6/src/bmm-skills/plan/bmad-sprint-planning/references/readiness-gate.md` | **Prompt**（LLM 判斷）。核心問題：「could a developer implement these epics without inventing decisions nothing records?」 |
| sprint-status 合併、status 不降級、drift | `scripts/sprint_plan.py`（v6.11+，37 個測試） | **程式** |
| Plan 核准與 frozen block | `bmad-build/step-02-plan.md` | Prompt（HALT 指示）；plan 檔落地可由人編輯 |
| Ticket 相依循環、drift、order_conflict | `skills/bmad-agent-po/scripts/tickets.py`（約 1,885 行） | **程式**；`validate-checks.md` 的語意檢查仍靠 LLM 子代理 |
| epics-and-stories final validation | v6.12.1：檢查全過才設 `status: final` | Prompt + frontmatter 狀態 |
| Review loop 上限 | step-04 計數 > 5 HALT | Prompt（計數寫在 frontmatter） |

### 1.5 Brownfield

v7 的立場很鮮明（`docs/existing-codebases/start-in-an-existing-codebase.md`）：既有知識已經寫在原始碼裡，文字描述反而造成「contradiction, ambiguity, and context-window bloat」。連原始的 greenfield PRD 都應封存，讓一般變更「should not even be able to find it by accident」。

- `bmad-project-context` 只在 `AGENTS.md` 寫一小段「已驗證」區塊，採用標準是「可從原始碼推導的就不存」。它取代了 `bmad-document-project` 產生的大量文件。
- `bmad-architecture` 在 brownfield 時「investigate before you decide」，承認既有慣例。
- `bmad-deep-recon` 可針對自家 repo 與 git history 研究，每個主張都附行號或 commit。

### 1.6 Token / context 成本

- **重。**
  - `bmad-build` 自身的 step 檔約 54 KB，加上 review prompts 約 19 KB。
  - 每次 Build 會開實作 subagent，再並行 3 到 4 個 review subagent（「must run at the same model capability」），倍數成本明顯。
  - 規劃層文件多：brief、PRD、addendum、memlog、UX ×2、architecture。
- **作者有意識地壓縮成本。**
  - 文件說 Sofia 一次讀入的實際上限是「a few tens of thousands of tokens, roughly a 40-page document」。
  - `bmad-shard-pro` 用來切長文件。
  - v6.12 起 Build 會先調查再決定 ceremony，小變更只寫兩節 spec。
  - subagent 只回傳短摘要，避免汙染主 context。

### 1.7 作者陳述的設計理由（README 與 docs）

- 「Coding assistants … often turn unstated assumptions into code」，所以要讓決策顯性化並持久保存。
- 「Right-sized process」：小變更直接 Build，大工程才補規劃。v7 甚至說「Too much planning costs documents nobody reads」。
- 多次以 A/B 實測修正 prompt。例如 v6.11 發現 adversarial reviewer 的「cynical」人設對抓 bug 率沒差，改成「至少 10 個具體發現」。這顯示 BMAD 正從「角色扮演」轉向「方法 + 評測」。

---

## 2. OpenSpec（Fission-AI）

### 2.1 版本

`@fission-ai/openspec` 1.16.0，npm 發布於 2026-10-30。1.15.0 起提供免 Node 的單一 binary。

### 2.2 目錄與產出

```
openspec/
  specs/<capability>/spec.md        # 現行真相（source of truth），behavior contract
  changes/<change-name>/
    proposal.md                      # Why / What Changes / Capabilities / Impact
    specs/<capability>/spec.md       # delta：ADDED / MODIFIED / REMOVED / RENAMED Requirements
    design.md                        # 選用
    tasks.md                         # checkbox，apply 會解析
    .openspec.yaml                   # schema、skip_specs 等
  changes/archive/YYYY-MM-DD-<name>/ # 歸檔後
  config.yaml                        # context: 注入每次 planning
```

Spec 格式為 `### Requirement:`（SHALL/MUST）加 `#### Scenario:`（WHEN/THEN）。

### 2.3 階段與驅動

- **工作流由 schema 宣告**（`schemas/spec-driven/schema.yaml`）：artifact 為 `proposal → specs → design → tasks`，各自有 `requires`，`apply.requires: [tasks]`，`tracks: tasks.md`。使用者可以自訂 schema 與模板（「OPSX」）。
- **Slash commands。** 預設 profile 為 `/opsx:explore`、`/opsx:propose`、`/opsx:apply`、`/opsx:archive`；擴充 profile 加上 `new`、`continue`、`ff`、`verify`、`bulk-archive`、`onboard`。
- **Prompt 由 CLI 動態提供。** agent 被指示呼叫 `openspec status --change X --json` 與 `openspec instructions <artifact> --change X --json` 取得當下規則與模板。也就是說 prompt 不全寫死在 slash command 檔，而是由 CLI 依 artifact graph 決定。這是 OpenSpec 最「工程化」的地方。
- **沒有 persona。**

### 2.4 Gate

| Gate | 強制方式 |
|---|---|
| `openspec validate`：每個 requirement 至少一個 scenario；零 delta 的 change 被拒（除非 `skip_specs: true`）；`--strict` 下 scenario 缺 WHEN/THEN、description > 500 字、Purpose 太短會失敗 | **程式**（`src/core/validation/validator.ts`） |
| `openspec archive` 先跑驗證；`--no-validate` 需要 `--yes`；有未完成 task 時 JSON 模式直接丟 `archive_tasks_incomplete`，互動模式要求確認 | **程式**（`src/core/archive.ts` 約 1454–1650 行） |
| Artifact 相依（`requires`） | CLI 回報 ready/blocked，但 **`status` 只看檔案是否存在**。propose 模板自己承認「status is file-existence only」，所以實際上是 prompt 加程式混合 |
| `/opsx:verify`（實作是否符合 spec） | **Prompt** |
| 文件明說「no rigid phase gates」，dependencies 是「enablers」 | 設計選擇 |

### 2.5 Brownfield

這是 OpenSpec 的核心賣點。`docs/existing-projects.md`：「You write specs only for what you're about to change.」`specs/` 一開始幾乎是空的，隨著每次 archive 合併 delta 而長大。`docs/concepts.md`：「Delta specs are the key concept that makes OpenSpec work for brownfield」。

### 2.6 Token 成本

**輕。** spec-driven schema 約 17 KB，propose 單份模板約 15 KB（檔案內有兩份）。每個 change 只讀相關的 capability：模板要求先用 `openspec show <spec> --json --no-scenarios` 取概覽，避免把整份 spec 拉進 context。官方建議實作前清空 context。

### 2.7 作者理由

- README 的哲學：「fluid not rigid / iterative not waterfall / easy not complex / built for brownfield not just greenfield」。
- `docs/opsx.md`：「Linear phases fight against how work actually happens.」
- 自比 Spec Kit：「Thorough but heavyweight. Rigid phase gates, lots of Markdown」。

---

## 3. Spec Kit（GitHub）

### 3.1 版本

`specify-cli` 1.3.0，PyPI 發布於 2026-11-03（main 為 `1.3.1.dev0`）。原始發表文章：Den Delimarsky，GitHub Blog，2025-09-02。

### 3.2 目錄與產出

```
.specify/memory/constitution.md                 # 專案原則（版本化、RATIFICATION/LAST_AMENDED 日期、Governance 節）
.specify/templates/、scripts/、extensions.yml
specs/NNN-feature/
  spec.md            # 只寫 what/why；[NEEDS CLARIFICATION] 標記
  plan.md            # Technical Context、Constitution Check gate、Complexity Tracking
  research.md        # Phase 0
  data-model.md、contracts/、quickstart.md      # Phase 1
  tasks.md           # 依 user story 分組，[P] 表示可平行
  checklists/*.md    # /speckit.checklist：「需求品質的單元測試」
```

### 3.3 階段與驅動

- **Slash commands / skills。** `/speckit.constitution` 只做一次；每個 feature 走 `specify → (clarify) → plan → (checklist) → tasks → (analyze) → implement → converge`。`converge` 是新的：比對程式碼與 spec/plan/tasks，**只會往 tasks.md 追加**剩餘工作，重複到回報 `Converged`。
- **腳本負責結構性工作。** 每個 command 的 frontmatter 指定 bash、PowerShell、Python 三套腳本（`create-new-feature`、`setup-plan`、`check-prerequisites`），負責建分支、資料夾和路徑。
- **擴充機制大。** 1.x 增加 extensions、hooks、presets、workflows（YAML 工作流引擎，具 `gate` step）、bundles、catalogs、MCP server。bug 修復和 idea assessment 是另裝的 extension。
- **沒有 persona。**

### 3.4 Gate

| Gate | 強制方式 |
|---|---|
| `plan-template.md` 的「Constitution Check — GATE: Must pass before Phase 0 research」；違反就寫進 Complexity Tracking | **Prompt / 模板** |
| `/speckit.analyze`：STRICTLY READ-ONLY；constitution 衝突一律 CRITICAL；有 CRITICAL 時「Recommend resolving」 | **Prompt**，只是建議 |
| `/speckit.implement`：checklist 有未勾項目就 STOP 並問 yes/no | **Prompt** |
| `check-prerequisites`：找不到 plan.md 或 tasks.md 就 `exit 1` | **程式**（只檢查存在與否） |
| `workflows/speckit/workflow.yml` 的 `review-spec`、`review-plan` 兩個 `type: gate`（approve/reject，reject 即 abort） | **程式**（`src/specify_cli/workflows/step/gate/`），但只在使用者用 `specify workflow run` 時生效 |

### 3.5 Brownfield

- `docs/how-to/existing-projects.md`：`specify init --here`；constitution 只寫「already true for the repository」的原則；第一個 feature 要選有邊界的變更，不要「document the entire existing system」。
- GitHub Blog 原文把「feature work in existing systems」列為最有威力的場景。
- **弱點：沒有像 OpenSpec 那樣的 living spec 合併。** `docs/how-to/spec-persistence.md` 明說 feature artifacts 交付後如何維護由團隊自選（三種模型，「None is the default」），而且「core workflow has no dedicated command that automatically reconciles」。

### 3.6 Token 成本

**最重的模板集。** 9 個 command 模板共約 128 KB（`specify.md` 19 KB、`implement.md` 13 KB、`analyze.md` 12 KB）。每個 feature 會產出 6 到 8 份文件，而 implement 要讀 constitution、spec、plan、tasks、data-model、contracts、research、quickstart、checklists。

### 3.7 作者理由

- `spec-driven.md` 的「The Power Inversion」：「Specifications don't serve code—code serves specifications.」Spec 是可再生程式碼的源頭。
- Constitution 九條（Library-First、CLI、Test-First 等），用模板約束 LLM 避免過度工程。
- Blog 強調把穩定的「what」和可變的「how」分開，人在每個 checkpoint 掌舵。

---

## 4. Fact-check 表

| # | 報告主張 | 判定 | 證據 |
|---|---|---|---|
| 1 | BMAD 模擬 Analyst、PM、Architect 角色 | **VERIFIED（需補充）** | `BMAD-METHOD/skills/bmad-agent-analyst/SKILL.md`：「You are Mary, the Business Analyst.」實際 persona 為 Mary（Analyst）、John（PM）、Winston（Architect）、Sally（UX）、Amelia（Dev），v7 另有 Sofia（PO）。SM/QA 已在 v6.3.0 併入 Amelia（`bmad-v6/CHANGELOG.md`：「Consolidate three agent personas into Developer agent (Amelia)」）。Persona 是同一個 agent 換 prompt，不是獨立的多代理；需要多視角時另有 `bmad-party-mode`。 |
| 2 | BMAD 有「Readiness Gates」，在寫程式前審查 stories 與 architecture | **部分 VERIFIED，名稱與現況過時** | 原名為 `bmad-check-implementation-readiness`（選單代碼 `IR`），v6.11.0 移除：「Folded into `bmad-sprint-planning`, which opens with a readiness gate (PASS/CONCERNS/FAIL)」（`bmad-v6/CHANGELOG.md`）。內容確實審 stories 與 architecture：「Architecture and UX decisions the stories rely on are recorded somewhere」（`readiness-gate.md`）。只有單一 gate，沒有複數的「Readiness Gates」，而且是 LLM 判斷。v7 main 已沒有 sprint-planning，readiness 改由 `tickets.py next/status` 加 Sofia 的 validate 處理。 |
| 3 | BMAD 擅長 fuzzy intent / 0→1 founder 專案 | **部分 VERIFIED；「founder」NOT FOUND；「專長於 0→1」CONTRADICTED** | 確實有模糊 intent 的工具：delivery loop 圖寫「a vague notion enters at Clarify」（`docs/images/bmad-delivery-loop.svg`），另有 forge-idea、prfaq、brainstorming。但 README 自稱同一套方法涵蓋「a weekend prototype and a system with years of history」；v7 docs 大幅著重 brownfield。Sofia 也「does not help you figure out what you want」（`docs/plan/choose-a-planning-path.md`）。repo 中找不到 founder 定位。 |
| 4 | OpenSpec 以 change 為中心、brownfield-first，有「durable change contracts」 | **前兩點 VERIFIED；「durable change contracts」NOT FOUND（報告自創用語）** | `OpenSpec/docs/concepts.md`：「brownfield-first — works with existing codebases, not just greenfield」。實際用語是 `changes/`、`specs/`、delta specs（ADDED/MODIFIED/REMOVED/RENAMED）、`archive`。「contract」指的是 spec：「A spec is a behavior contract, not an implementation plan.」durable 指的是 archive：「a durable record of why your system works」（`docs/faq.md`）。注意：change 本身是暫時的，歸檔後只有 delta 合進 specs 才是持久的。 |
| 5a | Spec Kit 專為 regulated 環境設計 | **CONTRADICTED（報告自創）** | README 只在 capability 表寫「Enforce organizational or regulatory standards」並導向 **Preset**；另一處「requiring regulatory traceability in plans」是 preset 範例。核心 SDD 不以 regulated 為定位；GitHub Blog 原文未提 regulated。 |
| 5b | 強調 governance 與 constitution | **VERIFIED** | `spec-kit/templates/commands/analyze.md`：「The project constitution … is **non-negotiable** within this analysis scope.」constitution 模板有 `## Governance` 節，含語意版本與修訂程序。 |
| 5c | 提供 full traceability audits | **NOT FOUND（誇大）** | 只有 `/speckit.analyze` 的 requirements→tasks 覆蓋對照（唯讀的 LLM 報告），以及 checklist 規定「≥80% of items MUST include at least one traceability reference」（`templates/commands/checklist.md`）。README 甚至寫「Catalog listings are not audits or endorsements」。沒有 audit trail 或程式化追溯功能。 |
| 6 | 目前版本與日期 | **VERIFIED（2026-11-04 查詢）** | BMAD stable v6.12.4（npm 2026-10-14），v7 alpha 在 main（commit 2026-11-02，README：「v7 release ETA is mid-November 2026」）。OpenSpec 1.16.0（npm 2026-10-30）。Spec Kit 1.3.0（PyPI 2026-11-03；`CHANGELOG.md`：「## [1.3.0] - 2026-11-03」）。 |

---

## 5. 技術優缺點比較

| 面向 | BMAD（v6.12 / v7） | OpenSpec | Spec Kit |
|---|---|---|---|
| 核心單位 | initiative → epic → story；一次 Build session 一個單位 | change（delta）→ 合併成 capability spec | feature 資料夾（`specs/NNN-x/`） |
| 長期真相 | 散在 PRD、architecture spine、AGENTS.md、memlog | **`openspec/specs/` 由 archive 累積**（最清楚） | 未定義，交給團隊選擇 |
| 程式強制 | 中：tracking 與相依腳本、render 快照 | **最強**：validator、archive 阻擋 | 弱到中：prereq 存在檢查、選用的 workflow gate |
| 人工檢查點 | Build CHECKPOINT、frozen-after-approval（設計最嚴謹） | 弱，刻意「fluid」 | 每步 review、workflow gate |
| 實作後驗證 | **最強**：多 lens 並行 review、triage、loopback、matrix 測試稽核 | `/opsx:verify`（prompt） | `converge`（只追加 task）、`analyze` |
| Token 成本 | 高（多 subagent） | **低** | 高（模板大、文件多） |
| 學習曲線與變動率 | 高；v6→v7 大量 breaking change | 低 | 中；extensions/presets 生態龐大 |
| Brownfield | v7 強：project-context 最小化、deep-recon 看 git | **原生**（delta） | 可用但無 delta 與合併 |

主要弱點：
- **BMAD**：版本變動極快，教學文章很快過時；persona 價值已被作者自己的 A/B 結果削弱；成本高；readiness 判斷靠 LLM。
- **OpenSpec**：`status` 只看檔案存在；verify 靠 prompt；delta 合併是以 requirement 標題文字匹配，改名時要用 RENAMED，容易出錯；沒有 review 機制。
- **Spec Kit**：feature spec 交付後會漂移；gate 幾乎都是 checklist prompt；constitution 預設九條偏特定架構觀（≤3 projects、Library-First）。

## 6. 改進構想（可借鏡、可組合）

1. **以 OpenSpec 的 delta + archive 作為長期 spec 層，以 BMAD Build 的 checkpoint 與 review 作為執行層。** 讓 `tasks.md` 完成且 review triage 沒有 `intent_gap` 時，才允許 `openspec archive`。
2. **把 prompt gate 程式化。** 例如 readiness 與 analyze 的輸出改成 JSON（PASS/FAIL + findings），由 CI 或 hook 決定是否放行；Spec Kit 的 workflow `gate` step 已提供這種範本。
3. **追溯性做成資料而非 prose。** requirement ID（OpenSpec 的 requirement 名、Spec Kit 的 FR-###）→ task → test 名稱 → commit，由腳本檢查覆蓋；參考 BMAD 的 matrix test audit「測試要實際跑過」。
4. **控制 context 成本。** 採用 OpenSpec 的「先 `--no-scenarios` 概覽、再讀全文」與 BMAD 的「subagent 只回短摘要、可推導的不存」兩條原則；Spec Kit 的大模板可用 preset 精簡。
5. **讓「durable」名副其實。** 把 BMAD v7 的 ADR 提案（deep-recon、retrospective 會從歷史提出 ADR）接到 OpenSpec 的 archive，讓決策理由與行為合約一起保存。

---

### 附註與限制

- 沒有執行任何 CLI，因此強制行為是從原始碼判讀，未經實測。
- GitHub Blog 內容經 WebFetch 摘要模型取得，未逐字核對全文。
- 未搜尋 OpenSpec 作者或 BMad Code 的個人部落格與 YouTube；設計理由以 repo 內文件為準。
- BMAD v7 是 alpha，本報告的 v7 細節可能在正式版前就改變。
