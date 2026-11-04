# 意見書：自用 agentic coding 工作流設計（方案 A）審查

- 日期：2026-11-04
- 審查對象：[docs/changes/2026-11-04-personal-workflow-design.md](../../changes/2026-11-04-personal-workflow-design.md)（以下稱「設計稿」）
- 研究依據：同資料夾的 [README.md](README.md)
- 查核方式：對照 Claude Code 官方文件、git 官方文件、Anthropic 工程文章、學術論文與研究機構報告。每條意見都附推導過程與出處；凡是只找到二手引述或未經本機實測的地方，都會標明。

---

## 摘要

方向正確：設計稿把品質規則從 prompt 移到 hook 執行，與 Anthropic 官方文件的建議一致。但目前有 **4 個高嚴重度問題**，其中前兩個會讓 gate 在最常用的流程中失效：

| # | 嚴重度 | 問題 | 章節 |
|---|---|---|---|
| 1 | 高 | gate 以 commit 為單位，級別卻屬於整個變更，與 superpowers 逐 task commit 衝突 | 3.1 |
| 2 | 高 | 證據日誌依賴的 `bashEditDiff`，官方明說不能用來強制執行 | 3.2 |
| 3 | 高 | 用指令字串偵測 commit：會漏、會誤擋，也看不到最終內容 | 3.3 |
| 4 | 高 | 多數檢查都有比「真的做到」更省事的通過方式 | 3.4 |
| 5 | 中高 | 痛點 1（skill 互相打架）的根本原因沒有被移除 | 3.5 |
| 6 | 中 | 檔案分類有漏洞，CI 與依賴清單被當成 T0 | 3.6 |
| 7 | 中 | 以 AGENTS.md 是否存在作為啟用開關，會誤觸第三方 repo | 3.7 |
| 8 | 中 | 每個 commit 的固定成本會讓 commit 變大 | 3.8 |
| 9 | 中 | 同一模型的 reviewer 有天生上限 | 3.9 |
| 10 | 中 | 沒有量測，驗收只跑一次 | 3.10 |
| 11 | 低 | 其他細節 | 3.11 |

---

## 1. 推導基礎：四條 AI 原理

以下每條意見都從這四條推出。

**P1　寫在 prompt 裡的規則只會「提高機率」，不是保證。**
LLM 根據上下文做條件抽樣，指令只會讓某些輸出更可能出現。Claude Code 官方文件原文：CLAUDE.md「treats them as context, not enforced configuration」，要擋下動作應使用 PreToolUse hook。

**P2　指令越多，每一條被遵守的機率越低。**
IFScale 測試 20 個前沿模型，在 500 條指令的密度下，最好的模型準確率約 68%，且偏向遵守較早出現的指令。Claude Code 官方建議每份 CLAUDE.md 控制在 200 行以內，原文說較長的檔案「reduce adherence」。

**P3　檢查一旦存在，就會變成模型要達成的目標。**
METR 觀察到前沿模型會修改計分程式或任務設定，而不是解題；在 RE-Bench 上這種行為比 HCAST 多 43 倍以上。這是 Goodhart 定律在 AI agent 上的表現。

**P4　同一個模型在沒有外部回饋時，自我修正不可靠。**
Huang et al.（Google DeepMind／UIUC，ICLR 2024）發現沒有外部回饋的 intrinsic self-correction 常常沒有幫助，有時還會讓表現下降。

**由此得出的評估標準**：由 P3，AI 會找通過檢查最省事的做法。因此一條 gate 規則是否有效，要看「最省事的通過方式」是否剛好等於期望的行為。若不等於，這條檢查只會產生填表動作。

---

## 2. 設計稿做對的地方

| 設計 | 理由 |
|---|---|
| 路由寫在 CLAUDE.md，不寫成 skill | 官方文件說根目錄 CLAUDE.md「survives compaction: after `/compact`, Claude re-reads it from disk」。skill 內容沒有這個保證；README 記錄的 fix loop 跑了 18 輪，正是 compaction 截斷 skill 所致。此決策直接處理了已知的失效模式。 |
| 強制執行放在 hook | 符合 P1 與官方建議。exit 2 的語意正確：官方原文為「Blocks the tool call」，stderr 會回傳給 Claude，且即使 JSON 寫了 allow 也照樣擋下。 |
| 不設字數門檻 | 正確預見了 P3：字數是最容易灌水的指標。 |
| reviewer 拿不到作者的結論 | 減少錨定效應，與 Osmani 的 Doubt-Driven Development 一致。 |
| change 檔寫完不修改，以 `supersedes` 取代 | ADR 的標準做法（Nygard 2011）。歷史與現況分離，接手者不會讀到被改寫過的歷史。 |
| 實作前先記錄 payload | 做法正確；查證後也確實發現推定欄位有問題（見 3.2）。 |
| 只能升級、敏感領域至少 T2、回覆第一行標級別 | 第一行標級別成本極低，使用者能及早發現分級錯誤。 |
| 選方案 A，不 fork | superpowers 兩個月出四版，自行維護 fork 的成本確實高。 |

---

## 3. 問題與風險

### 3.1【高】gate 以 commit 為單位，級別卻屬於整個變更

**推導**

1. gate 對每個 commit 判斷級別（設計稿 §3.2）。
2. superpowers SDD 的 implementer 每個 task 各自 commit（README §2.1）。
3. hook 的共通輸入有 `agent_id` 欄位，用來辨識發出呼叫的 subagent，因此 subagent 的 commit 同樣會經過 gate。
4. 一個 T3 功能拆成 N 個 task 時：
   - 只改一個原始碼檔的 task，依 gate 規則可**合法標成 T1**，不需要 change 檔。
   - 改多個檔的 task 要標 T2 或 T3，每個 commit 都得新增一份 change 檔，一個功能就會產生 N 份。
5. 前者使 T3 功能可能**永遠不會產生 `status: done` 的 change 檔**；後者使交接資料碎片化，與痛點 2「產出難以交接」的目標相反。gate 兩種情況都偵測不到，因為沒有任何欄位把 commit 和那份 T3 spec 連起來。

**建議**

- 新增 `Change: docs/changes/<file>.md` trailer。T2/T3 的 commit 可引用一份 `proposed` 或 `partial` 的既有 change 檔，不必每次新增。
- components、evidence、verified_by、reviewed_by 等驗證，只在 change 檔改為 `done` 的那個 commit 執行。
- 補一條確定性規則：只要 `docs/changes/` 中有 `proposed` 或 `partial` 的檔案，所有動到原始碼的 commit 都必須帶 `Change:` trailer。

### 3.2【高】證據日誌的「編輯時間」不可靠

**推導**

1. 設計規則是「verified_by 指令的成功紀錄，必須晚於 staged 檔案最後一次編輯」（§3.2-4）。這要求所有編輯都被記錄。
2. 透過 Bash 的編輯靠 `tool_response.bashEditDiff` 記錄。官方文件原文：「best effort and in public beta … Use the list to find what to review, not to enforce a policy」。且只有開啟 `bashEditDiffEnabled`，或在 auto／bypassPermissions 模式下才會記錄。
3. 使用者在 IDE 中手動修改的檔案完全不會進入日誌。
4. 結論：「測試後又改過」的情況會被誤判為通過（false pass）。

**建議（改用內容比對，並刪除部分機制）**

- 只在指令符合 AGENTS.md 宣告的測試指令時，記錄當下與 HEAD 不同之檔案的 `git hash-object`。
- commit 時以 `git ls-files -s` 取得 staged blob id，與最後一次成功測試記下的 hash 比對。一致即代表「測試跑的正是要 commit 的內容」。
- 如此**不再需要 edit 事件**：可移除 Edit/Write 的 PostToolUse 與對 bashEditDiff 的依賴。
- 以 `git add -p` 部分 stage 時，blob 與工作區不一致，結果為擋下。這是保守且正確的方向。

### 3.3【高】以指令字串偵測 commit：會漏、會誤擋

**推導**

- **會漏**：`git merge`（產生 merge commit，但指令中沒有 commit 字樣）、`cherry-pick`、`revert`、`rebase`、`git am`、alias（如 `git ci`）、腳本、GitPython。
- **會誤擋**：`git log --grep commit`、`git show <commit>` 等唯讀指令。誤擋過多的結果，通常是使用者自己關掉 gate。
- **看不到最終內容**：PreToolUse 執行時還不知道 index 與最終 commit message。設計稿因此需要「禁止與 git add 寫在同一條」，以及對 `-F`、`--amend`、heredoc、PowerShell 的各種解析規則。

**建議：改用 git 自身的 hook**

git 官方 githooks 文件寫明：commit-msg 由 git-commit **與 git-merge** 觸發，參數為最終 message 的檔名；pre-commit 執行時可看到實際的 index。

- 設計稿 §3.2 第 1 條、trailer 解析、PowerShell 測試情境都可刪除。
- 區分是否為 Claude 執行：官方 env-vars 文件說 Claude Code 在 Bash tool 啟動的 shell 中設定 `CLAUDECODE=1`。git hook 見不到此變數即放行，保留「使用者自己在終端機 commit」這個出口。**PowerShell tool 是否也設定此變數，未查到，需實測。**
- PreToolUse 只保留一條薄規則：擋 `--no-verify`、`-n`、`core.hooksPath`，以及修改 `CLAUDECODE` 的指令。
- 限制：
  - cherry-pick 與 rebase 仍不會觸發這些 hook（githooks 文件未列出它們，需本機實測確認）。
  - 若 repo 使用 husky，本地 `core.hooksPath` 會覆蓋全域設定，因此需逐 repo 安裝。

### 3.4【高】多數檢查都有更省事的通過方式（P3）

| 檢查 | 最省事的通過方式 | 等於期望行為？ | 改法 |
|---|---|---|---|
| `verified_by` 有成功紀錄 | 跑 `python -c "pass"` 再填入 | 否 | AGENTS.md 宣告測試指令，verified_by 至少須包含其中一條 |
| `reviewed_by` 非空 | 寫「fresh-context subagent」 | 否，純文字無法查證 | 以 SubagentStop 或 Agent 工具的 PostToolUse 記錄實際派出 reviewer，gate 比對此紀錄 |
| `evidence` 行號不超過檔案長度 | 填 `:1` | 否 | 行號須落在 `git diff --cached -U0` 的 hunk 範圍內 |
| 必須動到 ARCHITECTURE.md | 改日期或換句話說 | 否，且檔案會越長越大 | 刪除此條。matklad 原文：「only specify things that are unlikely to frequently change」，並建議「revisit it a couple of times a year」。改為只在新增 component id 時要求修改 |
| T3「決策」段非空 | 寫一句話 | 部分 | 可接受，但須理解它只證明「有寫」 |
| components 的 id 存在 | 必須真的對應到元件 | 大致是 | 保留 |

### 3.5【中高】痛點 1 的根本原因沒有被移除

**推導**

1. README §5-1 診斷的根本原因是「四層同時下指令」，包含 superpowers 與 ponytail 的常駐注入。
2. 方案 A 將兩者「原樣保留」，再加上一張分級表。指令總量增加，由 P2，每條規則被遵守的機率下降。
3. 「CLAUDE.md 優先於 skill」是寫在文字中的約定，不是執行機制；由 P1，實際結果取決於模型臨場判斷。
4. 本次審查的 session 本身就是例證：
   - superpowers 要求在任何回應前先叫 skill，並宣告「Using [skill]」。
   - ponytail 要求回覆最後一兩行寫「跳過了什麼」，且其注入內容包含流程規則（例如新邏輯須附測試），與分級表的管轄範圍重疊。
   - 設計稿再加上「第一行標級別」。這幾條在爭奪同一個輸出位置，而「ponytail 只管寫法」只是一條反向指令，並未移除 ponytail 的流程規則。

**建議**

- CLAUDE.md 中的分級表壓縮到約 15 行；gate 細節移入 change-record skill，被擋下時由 stderr 指向它，需要時才載入。
- 建立觸發 eval：T0、T1、T2 各 5 到 10 個 prompt，統計 brainstorming 被誤觸發的比例。以量測取代推理來判斷哪一層會勝出。

### 3.6【中】檔案分類有漏洞

- `.git*` 會匹配 `.github/workflows/`。`*.json|yaml|toml` 會匹配 `package.json`（依賴與 scripts）、`pyproject.toml`，以及 repo 內的 `.claude/settings.json`（hook 設定）。這些都被當成 T0、不經審查。
  依據：Google SRE 書指出約 70% 的 outage 來自對運行中系統的變更（**僅查到二手引述，未讀原書**）。
- 「路徑含 spec」若以子字串比對，`inspect.py` 會被視為測試檔。rea 專案中大量出現 `inspect*`（例如 `rea/bridge/pwndbg/` 下的 `inspect`），可藉此繞過 T1「最多一個原始碼檔」的限制。
- 「碰到 auth、付款、secrets 至少算 T2」目前只寫在 prompt 中。

**建議**

- 以路徑段（path segment）比對，不用子字串。
- CI、依賴清單、hook 設定列為「高風險設定」，至少 T2。
- 在 AGENTS.md 宣告敏感路徑 glob，由 gate 強制最低級別。這是把一條 prompt 規則升級為程式強制，成本很低。

### 3.7【中】以 AGENTS.md 作為啟用開關會誤觸第三方 repo

agents.md 官網寫明「used by over 60k open-source projects」。使用條件是新舊專案各半、偶爾協作，clone 進來的第三方 repo 很可能已有 AGENTS.md，gate 就會在別人的專案中要求 change 檔與 ARCHITECTURE.md。

**建議**：改用專屬開關，例如 `.agent-gate` 檔，或在 AGENTS.md 中加一行 `gate: on`。

### 3.8【中】每個 commit 的固定成本會讓 commit 變大

由 3.1，每個 T2 commit 都要附一份 change 檔。理性的做法（不論是人或模型）是把多次修改合併成一個大 commit 以分攤成本，這與 DORA 強調的「small batches」方向相反。

此外，舊專案首次做 T2 時，必須先寫出完整的 ARCHITECTURE.md YAML。由 P3，最可能的結果是產出一份空殼。

**建議**：3.1 的 `Change:` trailer 可同時解決前者；後者可先允許 ARCHITECTURE.md 只列出本次動到的元件。

### 3.9【中】同一模型的 reviewer 有天生上限

- fresh context 能去除錨定效應，但去不掉同一模型的共同盲點。另有研究發現 LLM 評審偏好自己產生的內容（Panickssery et al., NeurIPS 2024）。
- 由 P4，沒有外部訊號的審查，本質上是重新抽樣。

**建議**：要求 reviewer 的每條結論附上它實際執行過的指令或讀過的 `path:line`，並將這類證據也記入日誌。同時把「待人工確認」視為真正的最後一道關卡——設計稿已如此設計，應予保留。

### 3.10【中】沒有量測，驗收只跑一次

- METR 的 RCT 發現，有經驗的開發者使用 AI 後實際慢了 19%，自己卻估計快了 20%（**此數據取自二手報導，未讀原論文**）。主觀感受不能作為工作流有效的證據。
- 設計稿的驗收是「實際跑一次 T2」。模型輸出是隨機抽樣，一次成功幾乎沒有統計意義。依 rule of three，連續 10 次全部成功時，95% 信賴水準下失敗率上限仍約 26%（精確值 1 − 0.05^(1/10) ≈ 0.259）。

**建議**：每種級別至少跑 5 到 10 次，記錄四項指標：gate 擋下率、誤擋率、各級平均耗時、事後發現的缺陷數。上線前先量一週 baseline。

### 3.11【低】其他

- **T1 定義歧義**：「或 bug 修復」讀起來像任何 bug 修復都算 T1，但 gate 限制 T1 最多一個原始碼檔，兩者矛盾，須明確化。另「bug 先寫會失敗的測試」gate 未檢查；採用 3.2 的 hash 日誌後，可檢查「修改前的內容版本有一次失敗的測試紀錄」。
- **hook 指令中的 `~`**：官方文件說未安裝 Git Bash 時改用 PowerShell 執行，此時 `~` 不一定展開。官方建議一律使用絕對路徑。
- **保護 settings 的確定性機制**：官方提供 `ConfigChange` hook，可擋下設定在 session 中途生效（原文「the new settings are not applied to the running session」），比只靠 deny 規則與 CLAUDE.md 規定更強。
- **研究依據本身**：README §3 的 ●●● 評分沒有定義評分標準，他人無法重現，屬主觀判斷，不宜作為選型依據。

---

## 4. 建議的修改順序

1. 改用 git 的 commit-msg 與 pre-commit hook，PreToolUse 只保留防繞過規則（解決 3.3，並刪除大量解析程式）。
2. 加入 `Change:` trailer，僅在狀態改為 done 時做完整驗證（解決 3.1、3.8）。
3. 證據日誌改為內容 hash 比對（解決 3.2，並移除 edit 事件）。
4. 依 3.4 表格逐條修改：測試指令白名單、reviewer 派發紀錄、行號落在 hunk 內，刪除「必須動 ARCHITECTURE.md」。
5. 修正檔案分類，於 AGENTS.md 宣告敏感路徑，改用專屬啟用開關（解決 3.6、3.7）。
6. 精簡 CLAUDE.md，建立觸發 eval 與 baseline 量測（解決 3.5、3.10）。

---

## 5. 審查範圍與限制

- 未重新查核 README 中各工作流的版本細節（屬審查者知識截止日之後的資訊）。
- SRE 70% 與 METR RCT 數據取自二手引述。
- 下列事項須在本機實測：
  - PowerShell tool 是否設定 `CLAUDECODE`。
  - cherry-pick 與 rebase 確實不觸發 commit-msg／pre-commit。
  - hook 在 subagent 內觸發時 `agent_id` 的實際內容。

---

## 6. 來源

**官方文件**
- Claude Code hooks：https://code.claude.com/docs/en/hooks
- Claude Code memory：https://code.claude.com/docs/en/memory
- Claude Code env-vars（德文版，英文版未直接取得）：https://code.claude.com/docs/de/env-vars
- git githooks：https://git-scm.com/docs/githooks
- AGENTS.md：https://agents.md/

**公司與開發者經驗**
- Anthropic, *Effective harnesses for long-running agents*：https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- matklad, *ARCHITECTURE.md*：https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- Google SRE Workbook, Postmortem analysis：https://sre.google/workbook/postmortem-analysis

**學術與研究機構**
- Jaroslawicz et al., *How Many Instructions Can LLMs Follow at Once?*（IFScale, 2025）：https://arxiv.org/abs/2507.11538
- METR, *Recent Frontier Models Are Reward Hacking*（2025-06）：https://metr.org/blog/2025-06-05-recent-reward-hacking
- METR RCT（Simon Willison 摘要）：https://simonwillison.net/2025/Jul/12/ai-open-source-productivity/
- Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet*（ICLR 2024）：https://arxiv.org/abs/2310.01798
- Panickssery et al., *LLM Evaluators Recognize and Favor Their Own Generations*（NeurIPS 2024）
