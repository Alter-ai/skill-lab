# Superpowers（obra/superpowers）原始碼研究與事實查核

- 研究對象：`https://github.com/obra/superpowers`，完整 clone，HEAD `22f0b46`（2026-11-03，tag `v7.0.2`）
- 本地副本：`<redacted>/scratchpad/src/sp`
- 其他來源：`RELEASE-NOTES.md`、git history（`git log -S`）、作者部落格 blog.fsck.com（2025-10-09 "Superpowers"、2026-06-15 "Superpowers 6"、2026-10-09 "What a year"）
- 方法：只讀檔案，未執行 repo 內任何 script。下文的行號以 v7.0.2 為準。

---

## 1. 整體機制（端到端流程）

```
SessionStart hook（注入 using-superpowers）
  → brainstorming（釐清需求 → 選方案 → 寫 design doc → 使用者核准；HARD-GATE）
  → writing-plans（寫 docs/superpowers/plans/*.md，含 Global Constraints / Review Focus / 每個 Task 的 Interfaces）
  → 使用者選執行方式：
       Subagent-driven → subagent-driven-development（SDD）
       Native          → executing-plans（主代理自己做，結尾一次 reviewer）
  → 執行前 Setup：using-git-worktrees（先偵測，沒隔離時徵求同意）+ sdd-workspace + ledger + preflight 衝突掃描
  → 每個 task：task-brief → implementer subagent（TDD、commit、自我審查、寫 report 檔）
              → review-package → task reviewer（spec + quality 兩個 verdict）
              → 有 Critical/Important → fix loop（最多 5 輪，1–3 輪 resume 原 implementer，4–5 輪換更強模型的新 implementer）
  → final whole-branch review（最強模型，requesting-code-review/code-reviewer.md）→ 一次 fix wave → 一次 scoped re-review
  → 列出 "Rulings I made" → 刪除 workspace → finishing-a-development-branch（merge / PR / 保留 / 丟棄）
```

### 1.1 觸發機制：hook 注入 + description 文字 + 「1% 規則」

1. **Hook**：`hooks/hooks.json` 只註冊一個 `SessionStart` hook，matcher 為 `startup|clear|compact`，執行 `hooks/run-hook.cmd session-start`（Windows 有 `powershell` 版命令）。repo 內**沒有** `PreToolUse` / `PostToolUse` / `UserPromptSubmit` 等任何其他 hook。
2. `hooks/session-start` 用 bash builtin `read` 讀入 `skills/using-superpowers/SKILL.md` 全文，包在 `<EXTREMELY_IMPORTANT>You have superpowers. ...</EXTREMELY_IMPORTANT>` 裡，依平台輸出 `hookSpecificOutput.additionalContext`（Claude Code）、`additional_context`（Cursor）或 `additionalContext`（Copilot 等）。v7.0.2 改成不開任何子程序（Git Bash 下每次 fork 數十 ms）。
3. **using-superpowers**（65 行）是唯一常駐的 skill，核心是：
   - 「If you think there is even a 1% chance a skill might apply ... you ABSOLUTELY MUST invoke the skill.」（`skills/using-superpowers/SKILL.md:12`）
   - 在任何回應前（包括澄清問題、探索 codebase）先叫 skill；進 plan mode 前先 brainstorming。
   - Red Flags 表：列出 12 種「這只是簡單問題」「我先看一下檔案」之類的合理化念頭，一律視為違規。
   - `<SUBAGENT-STOP>`：被派出去的 subagent 忽略此 skill（避免子代理也去跑整套流程）。
   - 使用者指令（CLAUDE.md 等）優先於 skill。
4. **description 措辭**：其他 skill 都靠 frontmatter `description` 被模型「看到並決定載入」。描述刻意寫成觸發條件，而非功能摘要，例如 brainstorming：`"You MUST use this before any creative work - ... or planning anything new, in software or out of it"`；TDD：`Use when implementing any feature or bugfix, before writing implementation code`。`writing-skills/references/discovery.md`（"Skill Discovery Optimization"）專門教這種寫法。沒有 hook 的平台（Antigravity）完全靠 using-superpowers 的 description「Use when starting any conversation」讓模型自己載入（RELEASE-NOTES v7.0.0）。
5. **說服技巧**：作者 2025-10 部落格明說借用 Cialdini 的 authority / commitment / social proof，`writing-skills/references/persuasion-principles.md` 是對應文件；skill 文字大量使用全大寫、`<EXTREMELY-IMPORTANT>`、「Iron Law」、合理化對照表。

### 1.2 brainstorming（v7 重寫）

- 先判斷「需求是否已完整」：完整就直接做（例：把 icon 改成 cornflower blue）。
- 不完整時：先讀 codebase 再問；一次一個問題；先問「為什麼」；有可命名的選項時給選項加推薦；邊問邊「play back」200–300 字。
- 實作前必依序：列出 2–3 個方案讓使用者選 → 寫 design doc（小改動寫短版，專案寫完整版到 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` 並 commit）→ 使用者核准 → 只能接 `writing-plans`。
- 專案級 design doc 會派一個 **builder check** subagent（`builder-check-prompt.md`），以「要照這份文件施工的人」角度列出還缺什麼，然後只回問使用者一輪。
- `<HARD-GATE>`（`SKILL.md:269-283`）：核准前不寫產品碼、不 scaffold、不裝依賴。例外：使用者選擇跳過提問，或同意的 throwaway spike。
- 沒被明確要求時，第一則訊息結尾要提供「或者你想直接開始」的退出選項（v7.0.1 起，被點名呼叫則不提供）。
- 可選的 **Visual Companion**：本機 web server（`scripts/server.cjs`），v6 加上 per-session key、防 path traversal。

### 1.3 writing-plans（v6.4.2 大改）

- 計畫寫給「沒看過此 codebase 與 spec、但會寫慣用程式碼的工程師」（`SKILL.md:10`）。
- 必含 header：Goal / Architecture / Tech Stack / Spec 路徑 / **Global Constraints**（逐字複製 spec 的硬性數值）/ **Review Focus**（spec 隱含但無 task 測到的五個最可能出錯的輸入）。
- 每個 Task 有 `Files`、`Interfaces`（Consumes / Produces，精確簽章）、checkbox step。
- **Task Right-Sizing**（`SKILL.md:34-41`）：task 是「帶自己測試循環、值得 fresh reviewer 把關」的最小單位；setup/config/docs 併入需要它的 task。
- **Step Granularity**（`SKILL.md:43-50`）：step = 「一個動作，有可檢查的結果」（寫失敗測試 / 跑測試確認失敗 / 最小實作 / 跑測試確認通過 / commit）。
- v6.4.2 起不再寫完整程式碼，只寫簽章、測試斷言與 spec 數值；「A plan longer than the code it describes has written the code instead.」
- 計畫寫完做 5 項自我檢查（spec 覆蓋、step 掃描、型別一致、Review Focus、比例），**不派 subagent**。
- Handoff：讓使用者在 Subagent-driven 與 Native（executing-plans）之間二選一，並給推薦。

### 1.4 subagent-driven-development（SDD）的 dispatch 與 context

控制者（主代理）本身不寫碼，只協調：

| 角色 | 拿到什麼 context | 回傳什麼 |
|---|---|---|
| implementer | dispatch prompt 只有：1 行專案定位、**brief 檔路徑**（`scripts/task-brief PLAN N` 抽出該 task 全文寫成檔）、前面 task 的 interface/決定、控制者對歧義的裁決、report 檔路徑。禁止貼前面 task 的累積摘要；禁止叫 subagent 讀整份 plan。 | 完整報告寫入 `task-N-report.md`（含 TDD RED/GREEN 證據）；回傳 ≤15 行：Status（DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT）、commits、一行測試摘要、疑慮 |
| task reviewer | 三個路徑：brief、report、`scripts/review-package PLAN BASE HEAD` 產生的 diff 檔（commit list + stat + `git diff -U10`），外加逐字複製的 Global Constraints | Spec Compliance（✅/❌/⚠️ Cannot verify）、Strengths、Critical/Important/Minor、Task quality（Approved / Needs fixes）|
| re-reviewer | findings 清單 + brief + report + fix 範圍的 diff 檔 | 每條 ADDRESSED / NOT ADDRESSED，只看 fix diff |
| final reviewer | merge-base..HEAD 的 review package + ledger 裡 deferred minor 與 parked 項目 | 完整 code review |

重點設計：
- **所有工件走檔案**：`SKILL.md:183-185`「Everything you paste into a dispatch prompt ... stays resident in your context ... Hand artifacts over as files.」工件放在 git-ignored 的 `<repo>/.superpowers/sdd/<plan>/`。
- **Ledger**（`progress.md`）：對抗 context compaction；作者記錄到「已完成的 task 序列被整串重派」是最貴的失敗。
- **禁止 subagent 再派 subagent**（implementer 與 reviewer template 都有「You Do Not Dispatch Subagents」段落）。
- **禁止平行派 implementer**（`SKILL.md:235`）。
- **控制者不得預判 reviewer**：prompt 裡出現 "do not flag"、"at most Minor" 就是違規（`SKILL.md:285-290`）。
- **Reviewer 唯讀、不信任 report**：實作者的設計理由（"per YAGNI"）不能降低嚴重度；plan 本身規定的缺陷也要報為 Important（plan-mandated）。
- **持續執行**：只有四種情況可停下問人（不可逆操作、安全敏感、worktree 外的副作用如 push/merge、計畫壞到每條路都是猜）；其他一律自行裁決並在 ledger 寫 `Ruling: <決定> — <理由> — <錯了的代價>`，最後全部列給使用者。
- **Fix loop**（`references/fix-loop.md`）：每輪 = 一次修 + 一次 scoped re-review；最多 5 輪；第 1–3 輪 resume 原 implementer，第 4–5 輪新 implementer、至少高一級模型；第 5 輪後由控制者 adjudicate（park 或裁決），禁止提早裁決。Minor 不進 loop，記 ledger 給 final review。
- **Final review 只有一個 fix wave**（派一個 fixer 修全部 findings，不是一條一個）。

### 1.5 審查結構總覽

1. implementer 自我審查（不算數，只是先擋一輪）
2. 每 task 一個 task reviewer（spec + quality 兩個 verdict）
3. fix loop 的 scoped re-review
4. 整支 branch 的 final review（最強模型）＋ 一次 fix wave 的 re-review
5. brainstorming 階段的 builder check（審 design doc，不審程式）
6. `receiving-code-review`：要求對 review 意見做技術驗證，不盲從、不「表演式同意」

### 1.6 TDD 與 worktree

- `test-driven-development/SKILL.md:31-45` Iron Law：`NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`；「Write code before the test? Delete it. Start over.」「Delete means delete」。執行面只靠 prompt：implementer 被要求在 report 附 RED/GREEN 證據，reviewer 核對；沒有任何 hook 或 script 檢查測試先後。
- `using-git-worktrees`：Step 0 先偵測是否已在 linked worktree（比較 `git-dir` 與 `git-common-dir`，排除 submodule）；若在一般 checkout 且使用者沒宣告偏好，**先徵求同意**；優先用平台原生工具（如 `EnterWorktree`），否則 `git worktree add` 到 `.worktrees/`（需確認已被 gitignore）。在 SDD/executing-plans 的 Setup 階段呼叫，不在 brainstorming。
- `finishing-a-development-branch`：先跑完整測試 → 偵測環境 → 給固定 3 個選項（本地 merge / push 開 PR / 保留）或 detached HEAD 的 2 個；丟棄工作需使用者明確要求。

### 1.7 其他元件

- **commands / agents**：v5.0.0 之前有 `commands/brainstorm.md`、`write-plan.md`、`execute-plan.md` 與 `agents/code-reviewer.md`；v5.1.0（commit `f2cbfbe`，2026-05-04）刪除，改由 skill 本身處理（code-reviewer 移成 `requesting-code-review/code-reviewer.md` template）。
- **多平台**：`.claude-plugin`、`.codex-plugin`、`.cursor-plugin`、`.opencode`、`.pi`、`.hermes-plugin`、`.kimi-plugin`、`.antigravity-plugin`、`.muse-plugin`、`.devin-plugin`、`gemini-extension.json`；`using-superpowers/references/*-tools.md` 做工具對照。
- **diagnosing-superpowers**（新）：分析出錯 session、草擬 bug report。
- **Claude Code 專屬省錢模式**（`references/claude-code-tools.md`）：使用者要求時，派一個中階模型的 orchestrator subagent 跑整個 SDD，讓最貴的主 session 不做協調。
- **Skill 大小限制**：Claude Code compaction 後只重新附上每個 skill 的前 20,000 字元，所以 v7.0.1 把 SDD 細節拆進 `references/`，並加測試讓 SKILL.md 不得 ≥20,000 bytes（曾有 session 因 5 輪上限被截掉而跑了 18 輪 fix）。

---

## 2. 作者的設計理念（附出處）

| 主張 | 出處 |
|---|---|
| skill 是塑造代理行為的主要機制；bootstrap 只負責「讓模型去找 skill」 | blog.fsck.com 2025-10-09 "Superpowers"：「You have skills. They give you Superpowers.」 |
| 用說服心理學（Cialdini）讓模型更可靠，並以 subagent 做壓力測試驗證 skill | 同上；`skills/writing-skills/references/persuasion-principles.md`、`testing-skills-with-subagents.md` |
| subagent 的價值是隔離 context：「They should never inherit your session's context or history」 | `subagent-driven-development/SKILL.md:10` |
| token 很貴，v6 主軸是降成本 | blog 2026-06-15：「tokens are expensive and Superpowers uses a ton of them」；RELEASE-NOTES v6.0.0：約 2 倍快、少近 50% token |
| 合併兩個 reviewer 再省約 15% | blog 2026-06-15 |
| 「Turn count beats token price」：最便宜模型多步工作常多花 2–3 倍 turn，反而更貴 | `SKILL.md:164-170` |
| 停下來問人的成本 > 錯誤裁決的重工成本 | `SKILL.md:19-25`「a session parked on a question costs their whole day」 |
| 計畫不必寫完整程式碼，新一代模型能自己寫 body | RELEASE-NOTES v6.4.2（#2333）：取代 "zero context, questionable taste" |
| brainstorming 要更願意「讓路」 | blog 2026-10-09 "What a year"：「much happier to get out of the way」 |
| 實證驅動：大量用 eval（`evals/` drill submodule）量測措辭，例如 v7.0.2 盲評 filler question 從 41 降到 23 | RELEASE-NOTES v7.0.2；`docs/superpowers/specs/2026-06-10-*.md` |

---

## 3. 事實查核表

| # | 第三方說法 | 判定 | 證據 |
|---|---|---|---|
| 1 | 任務被切成 2–5 分鐘的原子任務 | **部分正確，已過時** | v4.0–v6.4.1 的 `writing-plans` 寫的是 **step**（不是 task）：「Each step is one action (2-5 minutes)」（v6.0.0 `writing-plans/SKILL.md:47`）。v6.4.2（2026-09-25）已改為「one action with a checkable result」（RELEASE-NOTES.md:147）。task 的大小由 Right-Sizing 決定（「smallest unit that carries its own test cycle」）。注意：`README.md:314` 仍寫「bite-sized tasks (2-5 minutes each)」，是說法來源，但與現行 skill 不一致。 |
| 2 | implementer subagent 被設定成「熱情但品味差、討厭測試的 junior engineer」 | **被誤植對象** | 這句話在 `README.md:42`，描述的是**計畫要寫得讓誰也能照做**：「enthusiastic junior engineer with poor taste, no judgement ... aversion to testing」。舊版 `writing-plans` 寫「zero context ... and questionable taste」（v6.0.0 `SKILL.md:10`），v6.4.2 已移除。`implementer-prompt.md` 從未用這種人設，只說「You are implementing Task N」，並鼓勵卡關時回報 BLOCKED。 |
| 3 | brainstorming 確認後會強制建立 git worktree | **現行版本不成立（歷史上是建議，非強制）** | v4.0.0 brainstorming 有「Ask: "Ready to set up for implementation?" / Use superpowers:using-git-worktrees」；2025-10 部落格也描述 brainstorming 後建 worktree。commit `7f2ee61`（2026-02-12，v4.3.0）移除。現行 brainstorming 核准後只能接 writing-plans（`brainstorming/SKILL.md:281-282`）；worktree 在執行階段 Setup 才做（`subagent-driven-development/SKILL.md:103-106`），且 `using-git-worktrees/SKILL.md:41-45` 要求先徵求同意，已在 worktree 中就不建。 |
| 4 | 先寫程式後寫測試就要刪掉重來；是 harness/hook 強制還是只靠 prompt？ | **文字正確；只靠 prompt** | `test-driven-development/SKILL.md:37`「Write code before the test? Delete it. Start over.」、`:43`「Delete means delete」。唯一 hook 是 SessionStart（`hooks/hooks.json`），沒有 PreToolUse 等攔截。間接檢查也只是 prompt：implementer report 要附 RED/GREEN 證據，reviewer 核對；`executing-plans/scripts/task-done` 只檢查測試指令是否通過，不檢查先後順序。 |
| 5 | 每個 task 有獨立 reviewer；早期兩個 reviewer（spec + quality），v6 合為一個 | **正確** | RELEASE-NOTES.md v6.0.0：「The two per-task reviewer prompts became one.」`spec-reviewer-prompt.md` 和 `code-quality-reviewer-prompt.md` 被 `task-reviewer-prompt.md` 取代，一次回傳兩個 verdict。blog 2026-06-15 說合併約再省 15%。另有最後一次 whole-branch review。 |
| 6 | v6 模型路由：Haiku 4.5 做小實作、Sonnet 5 做 review／高風險、Opus 5 做最終整支 branch review | **具體型號不成立；分層概念成立** | skill 只用與廠商無關的層級：機械式實作（1–2 檔、完整 spec）用 cheap model；整合／判斷用 standard；架構設計與 **final whole-branch review 用 most capable**；reviewer 依 diff 大小／風險選，中階為下限；fix loop 第 4–5 輪至少高一級；**每次 dispatch 必須明確指定 model**（`subagent-driven-development/SKILL.md:140-175`）。repo 的 skill 裡沒有「Haiku 4.5／Sonnet 5／Opus 5」的對應（`grep` 只在 writing-skills 引用的 Anthropic 文件與內部 eval spec 出現 haiku/sonnet/opus）。blog 2026-06-15 提到 Opus 當 coordinator、簡單 task 有條件用 Haiku，但沒有版本號。RELEASE-NOTES v6.4.2 提到 eval 跑在「Sonnet 5」上，那是測試環境，不是路由規則。 |
| 7 | 主代理把 task 文字寫成暫存檔，傳路徑給 worker，不直接貼文字 | **正確**（v6.0.0 起） | RELEASE-NOTES v6.0.0：「Diffs and task text move as files.」`scripts/task-brief` 檔頭註解：「so the task text never has to be pasted through the controller's context」。`SKILL.md:203-215`：dispatch 只放 brief 路徑；`SKILL.md:261-270`：reviewer 拿 review-package 檔。檔案放在 git-ignored 的 `.superpowers/sdd/<plan>/`，不是系統 temp。implementer 的報告也寫入檔案。 |
| 8 | 有沒有 v6？最新版與日期？ | **v6 存在；最新是 v7.0.2** | v6.0.0 於 2026-06-16 發布（tag 日期；blog "Superpowers 6" 2026-06-15）。之後有 6.0.1–6.4.2，再到 v7.0.0（2026-10-09，brainstorming 重寫）、v7.0.1（2026-10-21）、**v7.0.2（2026-11-03）**，`.claude-plugin/plugin.json` 的 `"version": "7.0.2"`。所以把 v6 稱為「目前版本」已經過時。 |

---

## 4. 優點

1. **context 管理講究**：brief、diff、report 都走檔案，dispatch 不貼歷史，控制者的 context 增長很少；ledger 讓 compaction 後還能接著做。
2. **把評審跟實作分開，並防止有人放水**：reviewer 唯讀、不信任實作者的說法、不得被控制者預判；plan 規定的缺陷也要報。這些都是從真實失敗案例修出來的規則。
3. **成本意識**：強制寫 model、Turn-count 原則、一個 reviewer、一次 fix wave、禁止 subagent 再派 subagent，並且用 eval 實測。
4. **流程閉環**：從需求到 merge 選項都有明確交接（每個 skill 結尾點名下一個 skill），使用者在 design doc 核准、執行方式選擇、merge 方式三個點介入。
5. **決策可審計**：「Ruling」一律寫 ledger、最後全部列給使用者，自主執行的同時保留追溯。
6. **跨平台**：同一套 skill 支援十餘種 harness，工具名稱已改成與廠商無關的描述。
7. **持續迭代、版本紀錄詳細**：RELEASE-NOTES 寫清楚每個改動背後的失敗案例與 eval 數據。

## 5. 缺點（技術面）

1. **Token／時間成本仍高**：每個 task 至少兩個 fresh context（implementer + reviewer），加上 fix loop 與 final review；作者自己的 spec（`2026-06-10-strict-cost-sdd-design.md`）把控制者列為最貴的位子（約 150 turn × 常駐 context）。v6 雖然省約 50%，小專案仍明顯比直接做貴。
2. **常駐 bootstrap 與過度觸發**：每次 startup / clear / compact 都注入完整 using-superpowers；「1% 規則」與「BEFORE ANY response」本質上傾向過度觸發，連簡單問題都要先查 skill。v7 brainstorming 加了「需求完整就直接做」與退出選項來補救，但根規則仍很強硬。
3. **僵化**：TDD「Delete means delete」不分情境；Red Flags 表把所有偏離都框成「合理化」，對探索性工作、既有無測試 codebase、UI 或資料管線不友善。例外（prototype、generated code、config）還要「ask your human partner」。
4. **全靠 prompt，沒有機械強制**：TDD 先後、HARD-GATE、不平行派 implementer、fix loop 上限都只存在文字中；compaction 截斷 20k 字元就曾讓 5 輪上限失效（v7.0.1 記錄的 18 輪案例）。能否遵守取決於模型能力，作者的 eval 也顯示 Sonnet 當控制者時明顯比 Opus 差。
5. **自主裁決的風險**：「Rulings, not stalls」讓控制者在 plan 有歧義時自行決定並繼續跑，錯誤裁決可能被後面多個 task 沿用，直到最後才給人看。
6. **只能序列執行**：implementer 不得平行，大計畫的牆鐘時間長。
7. **說服式語氣的副作用**：大量全大寫與 `EXTREMELY-IMPORTANT` 可能擠壓使用者自己的 CLAUDE.md 規則（雖然文字聲明使用者指令優先），在多個 plugin 並存時容易互相衝突。
8. **文件與實作脫節**：README 仍寫「2-5 minutes each」「enthusiastic junior engineer」，這正是第三方報告出錯的源頭。
9. **平台腳本複雜**：Windows／Git Bash／PowerShell／dash 的相容問題佔 release notes 很大比例，hook 失敗時 bootstrap 會靜默消失。

## 6. 改進建議

1. **把關鍵規則改成 harness 強制**：例如用 `PreToolUse` hook 在 implementer 第一次寫非測試檔前，檢查是否已有失敗中的測試紀錄；用 script 驗證 report 檔包含 RED/GREEN 區段；fix loop 輪數由 `task-done`／ledger script 計數並拒絕第 6 輪。
2. **觸發分級**：把「1% 規則」改成依任務大小分級（例：單檔、需求明確、不改行為 → 直接做），或用 `UserPromptSubmit` hook 先做輕量分類，再決定要注入哪些 skill，減少常駐 token 與過度觸發。
3. **TDD 例外清單明文化**：對 UI 微調、設定、探索性 spike、無測試基礎的舊專案給出明確降級路徑（例：characterization test 先行），而不是一律「刪掉重來」。
4. **具體模型對照表放在 per-harness reference**：skill 保持層級中立，但在 `claude-code-tools.md` 等檔案給目前建議的型號對照並標日期，減少控制者自己猜（也能避免第三方報告自行編造版本號）。
5. **高衝擊 Ruling 即時通知**：對會影響後續多個 task 的 ruling（load-bearing）提供非阻塞通知或在下一個 task 前做檢查點，而不是只在最後彙整。
6. **有條件平行**：對 plan 中 Interfaces 互不依賴、檔案不重疊的 task，允許在獨立 worktree 平行實作，再序列 review。
7. **README 與 skill 同步檢查**：加 CI 測試抓 README 中已從 skill 移除的說法（如「2-5 minutes」）。
8. **成本可視化**：在 ledger 記錄每個 dispatch 的 model 與 turn 數，結束時輸出總成本，讓使用者判斷 Subagent-driven 與 Native 的取捨。

---

## 附：關鍵檔案路徑（相對 repo 根目錄）

- `hooks/hooks.json`、`hooks/session-start`、`hooks/run-hook.cmd`
- `skills/using-superpowers/SKILL.md`（bootstrap 內容，1% 規則在第 12 行）
- `skills/brainstorming/SKILL.md`（HARD-GATE 269–283）、`builder-check-prompt.md`
- `skills/writing-plans/SKILL.md`（Right-Sizing 34–41、Step Granularity 43–50）
- `skills/subagent-driven-development/SKILL.md`（Model Selection 140–175、dispatch 規則 198–237）、`implementer-prompt.md`、`task-reviewer-prompt.md`、`re-review-prompt.md`、`references/fix-loop.md`、`references/final-review.md`、`scripts/task-brief`、`scripts/review-package`、`scripts/sdd-workspace`
- `skills/test-driven-development/SKILL.md`（Iron Law 31–45）
- `skills/using-git-worktrees/SKILL.md`（同意要求 41–45）
- `skills/requesting-code-review/SKILL.md`、`code-reviewer.md`
- `skills/finishing-a-development-branch/SKILL.md`
- `RELEASE-NOTES.md`（v6.0.0 起於第 334 行；v7.0.2 於第 3 行）
- `README.md:42`、`README.md:314`（第三方說法 1、2 的來源）
