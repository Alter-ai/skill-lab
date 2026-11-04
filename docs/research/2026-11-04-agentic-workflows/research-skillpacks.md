# 三套 agent skill pack 原始碼研究與第三方報告查核

研究日期：2026-11-04。所有原始碼以 `git clone --depth 1` 取得，只讀、未執行任何 script。

| 來源 | Repo | 讀到的 commit |
|---|---|---|
| Addy Osmani `agent-skills` | https://github.com/addyosmani/agent-skills | `301b02b`（2026-11-01），plugin v0.6.15 |
| Matt Pocock `skills` | https://github.com/mattpocock/skills | `4ae2317`（2026-10-31） |
| Lauren Tan `pstack` | https://github.com/cursor/plugins/tree/main/pstack（Cursor 官方 plugin repo 裡的一個資料夾，不是獨立 repo） | `bb68f23`（2026-11-03），pstack v0.15.36 |

**人名拼法**：正確是 **Addy Osmani**（`plugin.json` 的 `"author": { "name": "Addy Osmani" }`，GitHub 帳號 `addyosmani`）。第三方報告寫的 "Addi Osmani" 是錯字。

---

## 1. Addy Osmani — `agent-skills`

### 機制

- **結構**：`skills/`（25 個 SKILL.md，含 meta-skill `using-agent-skills`）、`agents/`（4 個 persona）、`references/`（7 份 checklist）、`commands/*.toml` 加 `.claude/commands/*.md`（9 個 slash command，分別給 Gemini/Antigravity 和 Claude Code 用）、`hooks/`、`scripts/`（驗證工具與 eval runner）、`evals/`（25 個 case 檔）。
- **生命週期與指令**（README 的 ASCII 圖）：DEFINE `/spec` → PLAN `/plan` → BUILD `/build` → VERIFY `/test` → REVIEW `/review` → SHIP `/ship`。另有三個橫跨流程的指令：`/constraints`、`/webperf`、`/code-simplify`。Claude Code 內建也有 `/review`，撞名時要用 `/agent-skills:review`。
- **`/build` 兩種模式**（`commands/build.toml`）：
  - 預設模式每次只做一個 task：RED 測試 → GREEN → 跑全套測試 → build → commit → 停。
  - `/build auto`（也接受 `all`）：spec 必須放在固定位置（`SPEC.md`、`docs/SPEC.md` 或 `spec/`）；先檢查 working tree 乾淨；需要時產生 `tasks/plan.md`；**只有一次人工核准**，而且「looks reasonable」這類含糊回覆不算核准；之後每個 task 各自 commit、只 stage 該 task 動到的檔。遇到以下情況會停下來問人：測試修不過或 build 壞了、spec 有歧義、碰到高風險或不可逆操作（auth、payments、destructive migration、secrets、deploy）。
- **`/constraints`**：最多問 4 題，然後在 repo 根目錄寫 **`CONSTRAINTS.md`**（大寫），內容有 Floor、各項門檻數值與理由、例外表（含 owner 與到期日）。依成本安排檢查放在哪一層（edit loop、task end、CI），並在 package.json 加 `check:fast/task/full`。子指令有 `check`、`guard`（抓偷降門檻、刪測試、加 suppress comment 的行為）、`ratchet`。
- **`/ship`**：fan-out orchestrator。在同一個 turn 平行派出 `code-reviewer`、`security-auditor`、`test-engineer` 三個 subagent，再由主 agent 合併結果、決定 GO/NO-GO，沒有 rollback plan 不能判 GO。規則是「personas don't invoke personas」。只有 ≤2 檔、<50 行、且沒碰 auth/payments/config 時，才可以跳過 fan-out。
- **`/webperf`**：單一 persona `web-performance-auditor`。有 Lighthouse/PSI/CrUX/trace 可用時走 Deep mode；否則走 Quick mode，所有 finding 標為「potential impact」，沒量到的指標寫 `not measured`，不准捏造數字。
- **每個 skill 的固定段落**：Overview → When to Use → Process → **Common Rationalizations**（藉口與反駁的表格）→ Red Flags → Verification。
- **Hooks**：`session-start.sh` 會注入 meta-skill，但**預設沒有接上**，註解說原因是 Claude Code/Codex 本來就靠 description 做路由，再加一層會變成兩個 router 疊在一起。另有 `sdd-cache-*` 和 `simplify-ignore` hook。
- **Eval**：三層。Tier 1 檢查結構；Tier 2 檢查 description 的路由詞彙有沒有互相碰撞，CI 會跑；Tier 3 對執行 trace 評分（見 `docs/comparison.md`）。

### 作者理由（https://addyosmani.com/blog/agent-skills/ ，2026-05-03）

- Agent 會走最短路徑，把 spec、測試、review 都跳過，skill 的作用是把這些步驟塞回去。原文："Process over prose. Workflows over reference."
- Anti-rationalization 表格的用意："pre-written rebuttals to lies the agent hasn't yet told"。
- 驗證不可省略，「Seems right」不算完成。靠 progressive disclosure 和 router 控制 context 用量。
- 素材來自 Google 工程文化（*Software Engineering at Google*、eng-practices）：Hyrum's Law、Beyonce Rule、Chesterton's Fence、Shift Left 等。

### 與使用者本機 `~/code/skill-lab/skills` 的比較

5 個本機版本（api-and-interface-design、ci-cd-and-automation、documentation-and-adrs、git-workflow-and-versioning、shipping-and-launch）的 `SOURCE.md` 都釘在**同一個 upstream commit `301b02b`**，所以內容是最新的。差異只在交叉引用，改成指向使用者本機有的 skill：
- `deprecation-and-migration` → ADR（`documentation-and-adrs`）
- `debugging-and-error-recovery` → `superpowers:systematic-debugging`
- `references/*.md` → `BACKLOG.md`（backlog skill）與內建 `security-review`
- git-workflow 的 description 拿掉了 "Use when making any code change"，避免過度觸發
- `documentation-and-adrs` 與 upstream 完全相同

這是正確的做法：只帶走 skill 本身，`references/` 沒有一起帶走，所以斷掉的連結都改掉了（upstream issue #361 講的就是這個可攜性問題）。

---

## 2. Matt Pocock — `skills`

### 機制

- **分類**：`engineering/`、`productivity/`、`misc/`、`in-progress/`、`deprecated/`。核心設計是把 skill 依「誰能叫用」分成兩類：
  - **User-invoked**：frontmatter 是 `disable-model-invocation: true`，只能由人打 `/name` 觸發，負責編排流程。
  - **Model-invoked**：保留 description，agent 可以自行觸發，裝的是可重用的工作紀律。
  - 規則：user-invoked skill 可以呼叫 model-invoked skill，但**不能呼叫另一個 user-invoked skill**。Codex 端用 `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false` 達到同樣效果。
- **grill 家族**：
  - `grill-me` 整份只有一行，內容是 "Call the Skill tool with "grilling""。
  - `grill-with-docs` 是 "Call the Skill tool twice, for "grilling" and "domain-modeling""。
  - 真正的機制在 `productivity/grilling`：把決策攤成 **design tree**，每一輪把「前提已確定」的 **frontier** 問題一次全部問完（編號，每題附建議答案，問法設計成回答「yes」就等於接受建議）。需要查事實時派 fresh-context subagent 去查，不問使用者。frontier 清空、使用者確認雙方理解一致之後才可以動手。
  - `domain-modeling` 負責 `GLOSSARY.md`（舊名是 `CONTEXT.md`）和 `docs/adr/`，會拿使用者用的詞去對照 glossary 和程式碼找矛盾。
- **`implement`**（user-invoked）：只有幾行。內容是：讀 ticket → 在事先講好的 seam 上用 `tdd` → 定期跑 typecheck 和單一測試檔，最後跑一次全套 → 交給 `code-review` → commit 到目前分支。`implement-spec` 是平行版本：用 task graph 讓多個 implementer subagent 同時處理 ready frontier 上的 task。
- **`tdd`**：測試只放在**事先跟使用者確認過的 seam**；以 vertical slice 當 tracer bullet；列出三個反模式：implementation-coupled、tautological、horizontal slicing；並且明確寫「Refactoring is not part of the loop」，重構歸 review 階段處理。
- **`code-review`**：兩個平行 subagent，Standards 軸（repo 規範加 Fowler smell baseline）和 Spec 軸（對照原始 issue/spec），用 fresh context 避免互相影響。
- **其他**：`to-spec`、`to-tickets`（tracer-bullet tickets 加 blocking edges）、`wayfinder`（跨 session 的決策 ticket 地圖）、`triage`、`retro`、`setup-matt-pocock-skills`（每個 repo 跑一次，設定 issue tracker、labels、docs 位置）。

### 作者理由（README）

README 依四種失敗模式組織：
1. 沒對齊需求 → grilling，引用 Pragmatic Programmer："No-one knows exactly what they want"
2. Agent 太囉嗦 → 用 DDD 的 ubiquitous language 建立共同詞彙
3. 程式不能動 → 建立回饋迴路，靠 TDD
4. 變成 ball of mud → 引 Ousterhout 的 deep modules，加上 `improve-codebase-architecture`

他也明確拿 GSD、BMAD、Spec-Kit 作對照：那些框架「own the process」會拿走控制權，所以他的 skill 刻意做得小、好改、可組合。user-invoked 和 model-invoked 的區分，是把 context 當成稀缺預算來管：user-invoked 不佔 context，代價是人要自己記得有這些 skill（`writing-for-agents/SKILL-MECHANICS.md`）。

### Orca 到底是什麼

在 Pocock 的 repo 裡 grep 不到 "orca"，web search 也找不到他做過 Orca 或公開背書的證據。最可能被誤植的是 **stablyai/orca**（https://github.com/stablyai/orca ，MIT 授權，「The AI Orchestrator for 100x builders」）：一個桌面加行動裝置的平行 agent orchestrator，每個 agent（Claude Code、Codex、OpenCode）各跑在獨立的 git worktree，附 Orca CLI。另外還有幾個同名但無關的專案：VirtusLab/orca、araa47/orca、geelen/orca。唯一的關聯是 claudekit.io 的 Orca 頁面把 Pocock 的 skills 列成可搭配的 skill 集合。**結論：Orca 不是 Pocock 做的**。

---

## 3. Lauren Tan（poteto）— `pstack`

### 作者確認

`pstack/plugin.json` 寫的是 `"author": { "name": "Lauren Tan" }`，LICENSE 是 "Copyright (c) 2026 Lauren Tan"，MIT 授權。README 自述在 Meta、Netflix、Cursor 工作過，也是 React core team 成員（React Compiler）。原始版本放在 Cursor 官方 `cursor/plugins` repo；GitHub 上另有很多社群 port（ahmedbenaw/pstack、michael-denyer/pstack-claude、ScriptedAlchemy/pstack-codex、pstack-t3 等），都不是作者本人維護的。

### 機制

- **入口是 `/poteto-mode`**：讀使用者的請求，從 **23 個 playbook** 裡挑一個（investigation、bug-fix、perf、hillclimb、feature、refactoring、prototype、shipping、autonomous-run、orchestrate、autopilot 等），把 playbook 的步驟逐字抄進 todo list，執行時依步驟需要觸發其他 skill。在 Claude Code 中的名稱是 `/pstack:poteto-mode`。
- **24 個 principle skill**（每個 skill 一條原則），例如 laziness-protocol、prove-it-works、fix-root-causes、build-the-lever、never-block-on-the-human、encode-lessons-in-structure。poteto-mode 要求回覆中寫出影響決策的原則名稱，而且只能引用本 session 實際讀過的原則。
- **多模型分工**：`/setup-pstack` 把每個角色對應到哪個模型寫成一條 rule（`pstack-models.mdc`，Claude Code 版則寫到 `~/.claude/rules/pstack-models.md`）。預設寫 code 用 grok、judgment 和 prose 用 opus 5.5。
- **`/arena`**（skill 名稱是單數 `arena`）分 6 個 phase：
  1. Frame：寫 3–6 條 rubric，候選者看不到 rubric
  2. Fan out：N 個背景 subagent，每個用自己的 worktree
  3. **Cross-judge**：一個 readonly 裁判，**必須來自與 parent 不同的模型家族**
  4. Pick：逐條 rubric 評分，跟裁判比對
  5. **Graft**：從落選候選挑一兩個優點，「by hand」重新設計後融入，不是機械式貼上；候選結果嚴重分歧就代表 Frame 寫得不夠清楚，要重來
  6. Verify
- **`/interrogate`**：沿用 arena 的 fan-out，但每個 adversary 只能回報**跑過、能重現**的 finding；風格類意見一律丟掉；不修 code。
- **`/show-me-your-work`**：單一 **TSV** 決策日誌，欄位是 `ts / phase / decision / why / evidence / result`，append-only。用 `scripts/log.sh` 寫入，它會清掉 tab 和換行，並在 `= + - @` 開頭的 cell 前加單引號，防 CSV/公式注入。結束前要拿 transcript 稽核日誌，錯的條目只能用新的一列覆蓋，不能修改舊列；最後由**另一個模型家族**審查整條決策軌跡。
- **`/blast-radius`**：重點不是列出 caller，而是找出「這次改動之所以安全的那一個事實」，把它的證據強度推到 5 級信心階梯的第 4 級（實際跑過真程式碼）。範圍大的改動改用 arena 處理。
- **`principle-prove-it-works`**：要檢查真實產物，不能靠 proxy、自我回報或「it compiles」；能寫成 script 的檢查就寫成 script。
- **`/unslop`**：有編號的 AI 腔清單，編號固定不重排（其他 skill 會引用編號），包括 AI vocabulary、"not just X but Y"、硬湊三點、em dash、粗體濫用、chatbot 用語等。
- **Subagent**：`poteto-agent`（被委派的 agent 必須先完整讀過 poteto-mode）和唯讀的 `comment-sicko`。

### 作者理由（README）

- "if you want to go fast, go deep first"：目標是寫更少但品質更高的 code。單一 agent 可信之後，才可能「fearless parallelism」。
- 她不相信規劃，原文："i don't believe in planning. the best spec is code."，所以 pstack 沒有 planning skill。
- 不同模型各有強項，所以 judge 和 reviewer 刻意找不同的模型家族。

---

## 4. 查核表

| # | 第三方報告說法 | 判定 | 證據 |
|---|---|---|---|
| 0 | 作者名 "Addi Osmani" | **CONTRADICTED** | 正確拼法是 Addy。`osmani/plugin.json`："name": "Addy Osmani" |
| 1 | 前 Google Chrome DX lead，現為 Anthropic engineer | **VERIFIED（但不完整）** | addyosmani.com/blog/agent-skills 的作者介紹寫 "Member of Technical Staff at Anthropic, where he works on Claude Code"；latent.space wiki 寫 "led Chrome's Developer Experience"。不過他離開 Google 前的最後職位是 Google Cloud AI 的 Director，只寫「Chrome DX lead」已經過時。 |
| 2 | 六階段指令 /spec /plan /build /verify /review /ship | **部分 CONTRADICTED** | 六個階段名稱正確（Define…Ship），但**沒有 `/verify` 指令**，VERIFY 階段對應的是 `/test`。README："/spec /plan /build /test /review /ship"。總共 9 個指令。 |
| 3a | `/build auto` 測試失敗時會暫停 | **VERIFIED** | `commands/build.toml`："a test can't be made to pass or the build breaks without an obvious fix"，條件列在 "Stop and ask the user (do not push through) when:" 之下 |
| 3b | `/constraints` 產生 constraints.md | **VERIFIED（檔名大小寫不同）** | `commands/constraints.toml`："Write CONSTRAINTS.md at the repo root" |
| 3c | `/web perf` | **CONTRADICTED（名稱）** | 實際指令是 `/webperf`，一個字。`commands/webperf.toml` |
| 3d | `/code simplify` 引用 Chesterton's Fence | **VERIFIED（名稱有連字號）** | 實際是 `/code-simplify`，它會呼叫 code-simplification skill；`skills/code-simplification/SKILL.md`："Step 1: Understand Before Touching (Chesterton's Fence)"。注意：command 檔本身沒提到 Chesterton，是在 skill 裡。 |
| 4 | Anti-rationalization 表格附反駁 | **VERIFIED** | 24 個 skill 有 "Common Rationalizations" 表。README："a table of common excuses agents use to skip steps" |
| 5 | Doubt-Driven Development：extract claims → challenge → reconcile → stop | **VERIFIED（步驟名稱不精確）** | 實際是 5 步：CLAIM → EXTRACT → DOUBT → RECONCILE → STOP。`skills/doubt-driven-development/SKILL.md`。細節：EXTRACT 是抽出「artifact + contract」，不是抽 claim；交給 reviewer 時刻意**不附 CLAIM**；最多跑 3 輪；每輪必須主動詢問使用者要不要用其他模型交叉審查。 |
| 6 | 四個 reviewer persona：staff engineer、test engineer、security auditor、web performance | **VERIFIED** | `agents/` 裡的 code-reviewer（"You are an experienced Staff Engineer"）、test-engineer、security-auditor、web-performance-auditor。注意：`/ship` 只 fan-out 前三個，web-perf 只能透過 `/webperf` 叫用。 |
| 7 | "Beyonce Rule" 出現在 Osmani 或 Pocock 的 skill | **VERIFIED（只出現在 Osmani）** | `skills/test-driven-development/SKILL.md:161`："If you liked it, you should have put a test on it." Pocock 和 pstack 中都 grep 不到。 |
| 8 | Pocock `implement` 有 `disableModelInvocation: true` | **CONTRADICTED（key 名稱）** | 實際 key 是 Claude Code 的 kebab-case 寫法，`skills/engineering/implement/SKILL.md:4`："disable-model-invocation: true"。作用：description 不載入 model context，agent 不會自動觸發，只能由人打 `/implement` 叫用，其他 skill 也無法呼叫它。 |
| 9 | grill-with-docs 會問約 30 題 | **NOT FOUND** | `grill-with-docs` 和 `grilling` 都沒有題數上限或目標數。結束條件是「frontier is empty」，題數取決於 design tree 有多大。「30+」只出現在第三方目錄網站。另外，目前版本是**每輪一次問完整個 frontier**，不是舊版的一次一題。 |
| 10a | Lauren Tan 是 Pstack 作者 | **VERIFIED** | `pstack/LICENSE`："Copyright (c) 2026 Lauren Tan"；plugin.json 的 author 也是 Lauren Tan |
| 10b | unslop | **VERIFIED** | `skills/unslop/SKILL.md`："Cut AI tells from any writing." |
| 10c | Arenas | **VERIFIED（skill 名稱是單數 `arena`）** | `skills/arena/SKILL.md`："Spawn N parallel candidates at the same task, pick a base, graft…" |
| 10d | cross-judge | **VERIFIED** | arena 的 Phase C："The judge is never from the parent's family" |
| 10e | graft | **VERIFIED** | arena 的 Phase E："Fold each graft in by hand… Don't paste mechanically." |
| 10f | "show me your work" TSV 決策日誌 | **VERIFIED** | `skills/show-me-your-work/SKILL.md`："A single TSV file, one row per decision." |
| 10g | blast radius | **VERIFIED** | `skills/blast-radius/SKILL.md`："Find what a change breaks somewhere else, before it ships." |
| 10h | "prove it works" | **VERIFIED** | `skills/principle-prove-it-works/SKILL.md`："Verify every task output by checking the real thing directly." |
| — | Orca 是 Pocock 的 CLI/orchestrator | **NOT FOUND／應為誤植** | Pocock 的 repo 中沒有 Orca。Orca 是 stablyai 的專案（https://github.com/stablyai/orca） |

---

## 5. 技術優缺點

### Osmani `agent-skills`
**優點**
- 涵蓋範圍最廣，從 idea 到 launch、observability、deprecation 都有。
- Anti-rationalization 和 Red Flags 是格式化的固定段落，有一致性。
- `/build auto` 的安全設計周到：只認固定位置的 spec、要求乾淨的 working tree、每個 task 獨立 commit、只 stage 該 task 的檔、含糊回覆不算核准。
- `/ship` 的 fan-out 加 merge 有明確的 NO-GO 預設規則。
- 有 in-repo 的 eval，會檢查路由碰撞，三套中只有它有。
- 支援的 host 最多。

**缺點**
- 25 個 skill 加 checklist 的 token 和認知負擔大；skill 一般長達 300 行以上。
- 單獨安裝某個 skill 時，`references/` 的連結會斷（#361）。
- 會跟 Claude Code 內建的 `/review` 撞名。
- persona 大多是同一個模型換角色扮演，盲點相同。唯一的跨模型機制在 doubt-driven，而且要使用者同意才會啟動。
- Process 偏重，小改動會被框架拖慢；雖然有 skip 條件，但要靠 agent 自己判斷。

### Pocock `skills`
**優點**
- 極度精簡、可組合。wrapper 一行就能指到 primitive，改一處全部生效。
- user-invoked 和 model-invoked 的區分把 context 當預算管理，概念清楚。
- grilling 的 frontier-round 設計能並行提問，又能尊重問題之間的依賴，也明確分工：「事實由 agent 自己查，決策交給人」。
- TDD 先約定 seam，避免過度測試。
- code-review 用兩軸、fresh context，避免互相污染。

**缺點**
- 沒有 in-repo eval，回歸要靠作者自己用。
- 綁定個人慣例：需要先跑 `setup-matt-pocock-skills`，並採用他的 issue tracker 和 GLOSSARY 慣例。
- Build 之後的階段（安全、上線、可觀測性）幾乎沒有。
- `implement` 太薄，品質幾乎完全取決於 tdd 和 code-review 這兩個 skill。
- grilling 沒有收斂上限，大型設計可能問太多輪。

### pstack
**優點**
- 驗證強度最高：證據必須跑過才算，adversary 的 finding 也要重現才保留，judge 刻意找跨模型家族。
- arena 的 graft 步驟要求人工重新設計後融入，不是平均各方案。
- TSV 決策日誌有 append-only 規則，結束前拿 transcript 稽核，並防公式注入。
- 「encode lessons in structure」把教訓落實成 lint 或 script，而不是多寫一段文字。
- 原則拆成 24 個小 skill，方便其他 skill 用名稱引用。

**缺點**
- 深度依賴 Cursor 和多模型環境（Task tool 的 model slug、bugbot、automations、`/loop`）；在 Claude Code 裡會跳過部分步驟。
- 預設要能使用 grok 和 opus 兩個家族；只有單一模型時，cross-judge 會被跳過。
- 規則文字密度極高。poteto-mode 的單一條規則常常是一大段，可讀性和維護成本都高。
- 明言不做 planning，對需求不清的工作需要另外搭配 grilling 類工具。
- 成本高：N 個候選加裁判加 adversary，token 用量是倍數成長。

---

## 6. 改進建議（針對使用者自己的 skill-lab）

1. **補上跨模型或 fresh-context 審查**：可借用 Osmani 的 doubt-driven（傳給 reviewer 時去掉 CLAIM，只給 artifact 和 contract）加上 pstack 的 cross-family judge。在 Claude Code 中至少可以做到「fresh-context subagent，而且不附自己的結論」。
2. **把 user-invoked 和 model-invoked 的區分帶進 skill-lab**：只有在有人叫用時才需要的 orchestrator（例如 backlog 的 sprint 收尾）可以設 `disable-model-invocation: true`，省下常駐的 description context。注意 key 一定要用 kebab-case。
3. **借用 pstack 的 TSV 決策日誌**：放進長時間或無人值守的任務（例如 `/build auto` 類流程），規則是 append-only，結束時拿 transcript 稽核。成本低，可審計性高。
4. **借用 blast-radius 的信心階梯**（說了 → 指出行號 → 推理 → 實際跑過 → 在 app 中重現）：可以寫進 shipping-and-launch 或 code review，要求證據至少到「實際跑過」那一級。
5. **在 skill-lab 加最小版 eval**：參考 Osmani 的 Tier 2，用 description 路由詞彙碰撞檢查，避免本機 skill（例如 git-workflow 和 shipping）互搶觸發詞。
6. **持續同步 upstream**：本機 5 個 Osmani skill 已釘在最新 commit `301b02b`；之後可以用 `SOURCE.md` 裡的 commit 做 diff 再同步。

---

## 未查證或限制

- 只讀 shallow clone 的最新版本，沒有追 git 歷史（例如 grilling 何時從一次一題改成整輪提問）。
- Osmani 的職稱來自他的 blog 作者介紹和 latent.space wiki，沒有找到 Anthropic 官方公告。
- Pocock 自己的影片和推文中有沒有提過 Orca 或「30 題」，沒有逐一查證。
- 所有 script（`log.sh`、`check-plan.mjs`、hooks）都沒有執行。
