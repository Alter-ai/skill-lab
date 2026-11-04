# Agentic coding 工作流比較（已核實版）

日期：2026-11-04。起點是一份第三方報告《Agentic Coding 方法論評估與選型策略報告》（以下稱「原報告」）。每項說法都對照了原始碼（shallow clone）或一手來源。各工作流的細節、檔案路徑與引文在同資料夾的四份研究筆記：

- [research-superpowers.md](research-superpowers.md)：obra/superpowers v7.0.2
- [research-spec-driven.md](research-spec-driven.md)：BMAD v6.12.4／v7 alpha、OpenSpec 1.16.0、Spec Kit 1.3.0
- [research-skillpacks.md](research-skillpacks.md)：addyosmani/agent-skills @301b02b、mattpocock/skills @4ae2317、pstack（cursor/plugins @bb68f23）
- [research-claims-and-landscape.md](research-claims-and-landscape.md)：數據查核與 2026 工作流全景

這類資料半年就會過時：BMAD v7 預計 11 月中發布，Superpowers 兩個月內出了 v6.4.2 到 v7.0.2。

---

## 1. 原報告查核結果

✅ 已證實　⚠️ 部分正確或已過時　❌ 與來源矛盾　❓ 查不到一手來源

### 名稱與人物
| 原報告說法 | 判定 | 實際情況 |
|---|---|---|
| 「Addi Osmani」 | ❌ | 正確拼法是 **Addy Osmani**。他做過 Chrome DX lead，在 Google 的最後職位是 Google Cloud AI Director，現在在 Anthropic 做 Claude Code。 |
| Orca CLI 是 Pocock 路線的一部分 | ❌ | Orca 是 Stably AI 的平行 agent 編排器（stablyai/orca），Pocock 的 repo 裡完全沒有提到它。 |
| Pstack 作者是 Lauren Tan | ✅ | 確認無誤（poteto，現在在 Cursor）。pstack 是 `cursor/plugins` repo 裡的一個資料夾，不是獨立的 repo。 |
| 模型名稱 Haiku 4.5／Sonnet 5／Opus 5 | ⚠️ | 這三個模型都存在，但現在已經是 legacy。目前的模型是 Opus 5.5、Sonnet 5.5、Haiku 5.5、Fable 5.1。 |

### Superpowers
| 原報告說法 | 判定 | 實際情況 |
|---|---|---|
| 任務切成 2–5 分鐘 | ⚠️ | 2–5 分鐘說的是 plan 裡的 **step**，不是 task，而且 v6.4.2 已經改成「one action with a checkable result」。README 還留著舊說法。 |
| implementer 被設定成「熱情但品味差、討厭測試的 junior」 | ❌ | 這段話出自 README，描述的是「計畫要寫到連這種人都能照做」，不是給 implementer 的人設。 |
| brainstorming 結束就強制建 worktree | ❌ | 這從來只是建議，v4.3.0 就拿掉了。現在是到執行階段才建，而且要先問使用者。 |
| 先寫實作就強制刪除 | ⚠️ | 規則確實有（「Delete it. Start over.」），但**只寫在 prompt 裡**。唯一的 hook 是 SessionStart，沒有任何機制實際攔截。 |
| v6 把兩個 reviewer 合成一個 | ✅ | v6.0.0 release notes 有寫，作者部落格說這樣再省了約 15%。 |
| v6 依 Haiku 4.5／Sonnet 5／Opus 5 分配模型 | ❌ | skill 只定義三個層級：cheap、standard、most capable。final review 用最強的那層，reviewer 至少用中階，每次 dispatch 都要指定模型。沒有寫死任何具體型號。 |
| 用檔案路徑傳任務，不貼內文 | ✅ | v6.0.0 起由 `scripts/task-brief`、`review-package` 寫進 `.superpowers/sdd/`。 |
| v6 是現行版 | ⚠️ | 最新是 v7.0.2（2026-11-03），v7 重寫了 brainstorming。 |

### BMAD／OpenSpec／Spec Kit
| 原報告說法 | 判定 | 實際情況 |
|---|---|---|
| BMAD 模擬 Analyst／PM／Architect | ✅ | 對應的 persona 是 Mary、John、Winston，加上 UX 的 Sally 和 Dev 的 Amelia。SM 和 QA 在 v6.3 已併入 Dev；v7 新增 PO 的 Sofia。所有 persona 都是同一個模型換 prompt。 |
| BMAD 有 Readiness Gates | ⚠️ | 原名是 `bmad-check-implementation-readiness`，v6.11 刪除後併進 sprint-planning 的開頭，v7 又拿掉了。這道關卡一直是由 LLM 判斷，不是程式。 |
| BMAD 專長是 0→1、模糊需求 | ⚠️ | 它有處理模糊想法的工具，但 README 同時宣稱適用「weekend prototype」到「years of history」，v7 還偏向既有程式碼庫。 |
| OpenSpec 以變更為導向、棕地優先 | ✅ | 每次變更放在 `changes/`，用 delta spec（ADDED/MODIFIED/REMOVED/RENAMED）描述，archive 時併入 `specs/`。 |
| OpenSpec 的「durable change contracts」 | ❓ | 查不到這個詞。官方說法是「behavior contract」。 |
| Spec Kit 專為高度監管環境設計 | ❌ | 這是原報告自己的詮釋。官方只說 preset 可以用來「Enforce organizational or regulatory standards」。 |
| Spec Kit 有完整可追溯審計 | ❓ | 只有一份由 LLM 產生的一致性報告，加上「≥80% checklist 項目要附追溯參照」這條規則。 |

### Addy Osmani agent-skills
| 原報告說法 | 判定 | 實際情況 |
|---|---|---|
| 六階段 `/spec /plan /build /verify /review /ship` | ⚠️ | 六個階段沒錯，但**沒有 `/verify`**，Verify 階段用的是 `/test`。指令總共 9 個。 |
| `/build auto` 測試失敗就停 | ✅ | 除了測試失敗，遇到 spec 有歧義或高風險操作也會停。 |
| `/constraints` 產生 constraints.md | ⚠️ | 檔名是大寫的 `CONSTRAINTS.md`。 |
| `/web perf`、`/code simplify` | ❌ | 實際名稱是 `/webperf`、`/code-simplify`。Chesterton's Fence 寫在 skill 裡，不在 command 裡。 |
| 反合理化表 | ✅ | 24 個 skill 都有 Common Rationalizations 表。 |
| Doubt-Driven Development | ⚠️ | 流程是 CLAIM → EXTRACT → DOUBT → RECONCILE → STOP。reviewer **拿不到原始主張**，最多跑 3 輪。 |
| 四大審查 persona | ✅ | `/ship` 只派出其中三個，web-perf 是由 `/webperf` 單獨使用。 |

### Matt Pocock skills
| 原報告說法 | 判定 | 實際情況 |
|---|---|---|
| Beyonce Rule 出自 Pocock | ❌ | 只出現在 Osmani 的 TDD skill 裡。 |
| `disableModelInvocation: true` | ❌ | 實際的 key 是 `disable-model-invocation: true`。設了之後只有人打 `/implement` 才會執行。 |
| Grill 會問約 30 題 | ❓ | 沒有題數設定。它每輪把當下能回答的問題一次問完，問到沒有問題為止。 |

### The Gray Cat 實測與其他數據
| 原報告說法 | 判定 | 實際情況 |
|---|---|---|
| The Gray Cat 實測，影片〈I Tested Superpowers v6 vs Grill Me〉（2026-09-08） | ✅ | 影片說明欄證實：兩邊都用 Opus 5，78 vs 148 分鐘，$34.04 vs $91.53（作者標明是 API 價估算），Superpowers 少用 53% token，而且沒有可見的 UI 缺陷。 |
| Pocock 路線的 156 分鐘、$96.01、$94.05、236/861 行 | ❓ | 說明欄沒有這些數字，影片本身沒看，所以無法判定。「校正後 $96.01」很可能是把作者對**更早 Osmani／Wayfinder 測試**的校正搬錯了地方。 |
| 8 個 worker 中有 5 個沒載入 /implement | ❌ | 影片說法是「只有 3/8 拿到完整的 implement skill」，作者把原因歸給**自己的叫用方式**，不是工作流本身的缺陷。原報告把它延伸成「harness 比模型重要」，這是過度推論。 |
| 1000 行規則 ≈ 每輪 7000 token | ❓ | 只找到社群部落格的估算（7k–10k），沒有一手來源。 |
| agent-skills.io、64/1024 字元、500 行 | ⚠️ | 網域是 **agentskills.io**。字元上限正確，500 行和 5000 token 是建議值。授權是 Apache 2.0（code）加 CC-BY-4.0（docs）。 |
| AGENTS.md／MCP 在 AAIF，A2A 在 Linux Foundation | ✅ | AAIF 成立於 2025-12-09。A2A 於 2025-06 捐給 Linux Foundation。 |
| 35% skills 有瑕疵、13% 含注入或惡意程式 | ⚠️ | 出處是 Snyk ToxicSkills：36.82% 有瑕疵，13.4% 屬 critical。後者也包含外洩 secret，不只是注入或惡意程式。 |
| IBM 合規報表加總錯誤 | ❓ | 查不到出處。 |
| Depot Cloud 沙盒 | ⚠️ | Depot 有 agent sandbox 產品，但產品名稱不是「Depot Cloud」。 |
| 記憶模型對應到 RAG／memory／skills | ⚠️ | 這個分類源自 CoALA 論文（Princeton，2023），對應到 RAG/memory/skills 是社群的延伸說法。 |

**整體評價**：原報告的大方向可以參考：各工作流在 SDLC 中各有定位、subagent 用來隔離 context、Superpowers v6 的省 token 機制。但大約一半的具體細節是錯的、過時的，或查不到出處，包括指令名、人名、版本、檔名和 benchmark 細節。它的寫法也把很多「只寫在 prompt 裡的規則」描述成「harness 強制」，這是最需要注意的誤導。

---

## 2. 各工作流如何運作

### 2.1 技能框架類

**Superpowers（Jesse Vincent）**
- **觸發**：SessionStart hook 把 `using-superpowers` 全文注入，內容包括「1% 機會就必須叫 skill」和合理化對照表。其他 skill 靠 description 措辭由模型自行觸發。作者明說借用了 Cialdini 的說服原則。
- **流程**：brainstorming（HARD-GATE）→ writing-plans → 選擇執行方式 → subagent-driven-development。每個 task 依序是：task-brief 檔 → implementer（TDD、commit、report 檔）→ 一個 reviewer 給出 spec 和 quality 兩個 verdict → fix loop（最多 5 輪，第 4–5 輪換更強的模型）→ 整支 branch 的 final review → finishing-a-development-branch。
- **設計邏輯**：用 subagent 隔離 context；「turn 數比 token 單價重要」，所以不一味用最便宜的模型；遇到歧義由控制者自己裁決並寫進 ledger，不停下來等人，因為「卡住一整天比錯一次貴」。
- **限制**：所有 gate 都只靠 prompt。有一次 compaction 把 skill 截斷，導致 5 輪上限失效，fix loop 跑了 18 輪。

**Addy Osmani agent-skills**
- **組成**：25 個 skill、9 個 command、4 個 persona。每個 skill 都有固定段落：Overview → When to Use → Process → Common Rationalizations → Red Flags → Verification。
- **`/build auto`**：spec 要放在固定位置、working tree 必須乾淨、只核准一次（「looks reasonable」不算核准）、每個 task 各自 commit。
- **`/ship`**：平行派出三個 persona，NO-GO 是預設結果，沒有 rollback plan 不能判 GO。
- **eval**：三層，CI 會檢查各 skill 的 description 有沒有搶同一批觸發詞。
- **設計邏輯**：「Process over prose」。agent 會走最短路徑，所以要用流程把 spec、測試、review 塞回去；反合理化表是「事先寫好的反駁」。session-start hook 刻意**不預設接上**，作者認為兩層路由疊在一起會互相干擾。

**Matt Pocock skills**
- **兩類 skill**：
  - user-invoked：設 `disable-model-invocation: true`，負責編排流程，不佔 context。
  - model-invoked：可重用的工作紀律。
  - user-invoked 不能呼叫另一個 user-invoked。
- **grilling**：把決策攤成一棵 design tree，每輪把前提已確定的問題一次問完，每題附建議答案。事實由 subagent 去查，只有決策交給人。
- **domain-modeling**：維護 GLOSSARY.md 和 ADR。
- **tdd**：先和使用者約定 seam，再在 seam 上寫測試；重構不放在 TDD 迴圈裡。
- **code-review**：兩個 fresh-context subagent，一個看 Standards，一個看 Spec。
- **設計邏輯**：明確反對 BMAD、Spec Kit 這類「把流程拿走」的框架。他的 skill 刻意做得小、好改、可組合，並把 context 當成預算管理。

**pstack（Lauren Tan）**
- **入口**：`/poteto-mode` 從 23 個 playbook 中挑一個，把步驟逐字抄進 todo；另有 24 個「一條原則一個 skill」的 principle skill。
- **`/arena`**：N 個 worktree 各做一份候選 → 由**不同模型家族**的裁判評分 → 從落選者挑優點人工 graft 進最佳解。
- **`/show-me-your-work`**：append-only 的 TSV 決策日誌，結束前拿 transcript 稽核。
- **`/blast-radius`**：找出「這個改動之所以安全的那一個事實」，並把證據推到「實際跑過」。
- **設計邏輯**：「go fast by going deep first」；不做規劃（「the best spec is code」）；不同模型盲點不同，所以裁判要跨模型家族。

### 2.2 規格驅動類

**BMAD-METHOD**
- **persona**：都是同一個模型換 prompt。
- **文件鏈**：brief → PRD → architecture → epics/stories。
- **Build 階段**：有 checkpoint，規格核准後凍結；之後多個 lens 平行 review，再做 triage 和 loopback。
- **程式強制的部分**：只有 `sprint_plan.py`／`tickets.py` 的結構與相依檢查。
- **主要風險**：變動極快，v6 到 v7 有大量 breaking change，教學文章很快過時。

**OpenSpec**
- **流程**：每次變更是 `changes/<id>/` 底下的 proposal、tasks 和 delta spec，archive 後併入 `openspec/specs/`，形成持續存在的「現況規格」。
- **程式強制的部分**：`openspec validate`／`archive` 是三者中最強的，task 沒完成就不能 archive。
- **成本**：token 最低。
- **弱點**：verify 只靠 prompt；delta 是用 requirement 標題文字比對來合併，改名容易出錯。

**Spec Kit（GitHub）**
- **流程**：constitution → `/specify` → `/plan` → `/tasks` → `/implement`，另有 `/analyze` 檢查一致性。
- **程式強制的部分**：prerequisite 腳本只檢查檔案存不存在；選用的 workflow 有 gate 步驟。
- **弱點**：沒有合併後的長期 spec，feature spec 交付後就會漂移；模板大，token 成本高。

### 2.3 其他值得知道的路線（未讀原始碼，只確認存在與核心機制）
- **GSD**：PROJECT/ROADMAP/STATE 文件，每個任務開新 context。
- **HumanLayer RPI**：Research → Plan → Implement，每段刻意壓縮 context。
- **Ralph loop**：同一個 prompt 無限迴圈，進度存在檔案和 git。
- **Compound Engineering（Every）**：每輪把教訓寫回規則和 skill。
- **Kiro**：EARS 格式的 requirements。
- **Claude Code plan mode**：內建的唯讀規劃模式。

---

## 3. 技術比較

評分：●●● 強　●● 中　● 弱　— 無。這是依第 2 節讀過原始碼後的**主觀判斷**，沒有量化標準，不能直接拿來當選型依據。

| 面向 | Superpowers | Osmani | Pocock | pstack | BMAD | OpenSpec | Spec Kit |
|---|---|---|---|---|---|---|---|
| 需求釐清 | ●●● brainstorming | ●● `/spec`、`/constraints` | ●●● grilling | — 刻意不做 | ●●● 多 persona | ● proposal | ●● specify/clarify |
| 長期規格／交接文件 | ● spec＋plan 檔散在 docs/ | ● SPEC.md | ●● GLOSSARY＋ADR | ●● TSV 決策日誌 | ●● PRD／architecture | ●●● specs/ 累積 | ● 每個 feature 一份，會漂移 |
| 執行時的 context 管理 | ●●● 路徑傳遞＋ledger | ●● | ●● | ●● | ●● | ●●● | ● |
| 測試紀律 | ●●● 但僵化 | ●●● | ●●● 先約定 seam | ●●● 證據要跑過 | ●● | ● | ●● |
| 獨立審查 | ●●● 每 task＋final | ●●● 三 persona | ●● 兩軸 | ●●● 跨模型家族 | ●●● 多 lens | ● | ● |
| 程式強制（非 prompt） | ● | ●（CI 檢查路由碰撞） | ● | ●●（log.sh） | ●● | ●●● | ●● |
| 成本 | 中高 | 中 | 低 | 高 | 高 | **低** | 高 |
| 與其他 skill 共存 | ● 常駐注入，語氣強硬 | ●● | ●●● | ● 綁 Cursor | ● 自成一套 | ●●● | ●● |

**七套共通的弱點**：品質關卡幾乎都只寫在 prompt 裡。真正由程式擋下的只有 OpenSpec 的 validate/archive、BMAD 的相依腳本，以及 Spec Kit 的 prerequisite 檢查。原報告說的「harness 比模型重要」方向沒錯，但目前沒有一套真的把 harness 做成強制。

---

## 4. 各自可以改進的地方

| 工作流 | 主要缺點 | 可行的改善 |
|---|---|---|
| Superpowers | 1% 規則容易過度觸發；TDD 一律刪掉重來；gate 只靠 prompt；ruling 到最後才給人看 | 依風險分級觸發；把 TDD 例外寫成明文清單；用 hook 或腳本數 fix loop 輪數、檢查 RED/GREEN 證據；影響多個 task 的 ruling 即時通知 |
| Osmani | 25 個 skill 太重；`/review` 和內建指令撞名；persona 都是同一個模型 | 只挑需要的 skill（你的 skill-lab 已經這樣做）；審查時不把原始主張交給 reviewer |
| Pocock | 沒有 eval；Build 之後的階段（安全、上線）沒有；grilling 沒有收斂上限 | 每輪設題數上限；接上 shipping 類 skill |
| pstack | 綁 Cursor 和多模型；成本高 | 在 Claude Code 中用「fresh-context＋不附結論」近似跨模型審查；arena 只用在高風險任務 |
| BMAD | 成本高；版本變動快；persona 的價值已被作者自己的 A/B 測試削弱 | 只借用凍結規格加 checkpoint 這個概念 |
| OpenSpec | 沒有 review；用標題文字比對合併 | 搭配一個 reviewer；requirement 改用 ID |
| Spec Kit | spec 會漂移；模板大 | 用 preset 精簡；加入 delta 合併 |

---

## 5. 對你的意義

依你目前回答的條件（個人為主、偶爾協作；新舊專案各半；依風險分級；痛點是 skill 互相打架、產出難以交接、品質不穩），結論如下：

1. **skill 互相打架**的根源是 Superpowers 的常駐注入、ponytail 的常駐規則、個人 skill 和 CLAUDE.md 四層同時下指令。值得借鏡的有兩個：Pocock 的「user-invoked vs model-invoked」分類，以及 Osmani「不預設接上 session hook」的做法。另外要把「誰負責哪個階段」寫成單一路由表。你的 CLAUDE.md 已經有雛形。
2. **產出難以交接**：OpenSpec「changes → 累積成 specs/」的模型最適合讓人和其他 AI 接手。再加上 Pocock 的 GLOSSARY／ADR，以及你剛做好的 ARCHITECTURE.md（人看的 Mermaid 加 AI 讀的 YAML）。
3. **品質不穩**：七套的共同弱點都是 prompt 規則。改善方向是把少數幾條關鍵規則**程式化**（hook 或腳本），再採用 pstack「證據必須實際跑過」和 Osmani 的 NO-GO 預設。
4. **依風險分級**：七套都沒有把它做好。可以把你 CLAUDE.md 的第 1–3 條升級成一個明確的分級器，決定要走哪條路。
