# 第三方報告事實查核與 2026 AI coding 工作流全景

查核日期：2026-11-04。星數取自 GitHub API 當日數值。

## 一、逐條查核

### A. The Gray Cat 基準測試 — 部分驗證（核心數字對，細節無法從一手來源確認）

- 來源：YouTube 頻道 **The Gray Cat**（@thegraytcat），影片〈I Tested Superpowers v6 vs Grill Me: The Results Are Shocking〉，2026-09-08 發佈，約 6 萬次觀看。https://www.youtube.com/watch?v=d8lxLTQhmPo
- 影片說明欄（一手）確認：
  - Opus 5 主控：「with Opus 5 controlling each run」 ✔
  - 時間：「Superpowers stopped after 78 active minutes; the Pocock retry took 148」 ✔
  - 成本：「API-equivalent costs were $34.04 and $91.53」 ✔（作者強調用訂閱跑，金額是按 API 價格**估算**）
  - token：「Superpowers v6 used 53% fewer tokens than my Matt Pocock retry」。報告的 55.9M 和 119.7M 換算正好少 53.3%，數字自洽，但說明欄沒有列出絕對值。
  - UI 缺陷：「passed my four-take app check without a visible UI defect」 ✔（報告寫「0 UI defects」，原文是「沒有看得見的缺陷」，語氣較弱）
  - 「5 of 8 workers failed to trigger /implement」：原文是「Only three of eight workers received the full implement skill」，並說是**作者自己呼叫方式出了問題**，不是 skill 本身沒有觸發。報告把責任歸給工作流，屬於誤述。
  - 說明欄只寫「Grill with Docs route」，**沒有提到 Orca CLI**。
- 說明欄**沒有**這些數字：156 分鐘（含修復）、$96.01、$94.05、236 行和 861 行。要查只能看影片本身或逐字稿，這次未查。
- 報告內部矛盾的可能解釋：說明欄寫「I compare the new runs with the earlier Wayfinder and Addy Osmani results, including corrected costs」。所以「corrected」指的是**前一支影片（Pocock vs Osmani）的 Osmani 和 Wayfinder 成本**被修正，不是指 Pocock 這次的 $91.53。報告把「Osmani corrected to 96.01」和 Pocock 的成本混在一起，很可能是轉述時張冠李戴（推論，未驗證）。
- 作者自己的結論：「it does not establish a universal winner」，只是單一功能、單次測試。
- 參考：Superpowers 6 官方發佈文章另外宣稱約快 50%、省約 60% token，這是廠商自己的評測。https://blog.fsck.com/2026/06/15/Superpowers-6/

### B. 「約 1000 行規則每輪約 7000 tokens」 — 查無官方來源（屬社群估算）

- 這個說法出自開發者 Abd Rahman Saber Abdo 的文章，經 gentic.news / DEV 轉貼，估計範圍是 7k 到 10k tokens。https://dev.to/gentic_news/claudemd-wastes-7k-tokens-per-turn-skills-cut-to-50-41hf
- Anthropic 官方沒有這個數字。換算約每行 7 tokens，數量級合理，但會隨語言而變，中文每行的 token 數更多。
- 補充：「每輪」的說法要加註。CLAUDE.md 在每次請求都會佔用 context，但有 prompt cache，實際成本遠低於全價。

### C. Agent Skills 開放標準 — 已驗證，但網域名稱有誤

- 網域是 **agentskills.io**，報告寫的「agent-skills.io」是錯的。https://agentskills.io/specification
- 規格原文：
  - name：「Max 64 characters. Lowercase letters, numbers, and hyphens only.」 ✔
  - description：「Max 1024 characters. Non-empty.」 ✔
  - 本文長度：「Keep your main `SKILL.md` under 500 lines.」，並寫「Instructions (< 5000 tokens recommended)」 ✔（兩者都是建議，不是硬性限制）
- 授權：README 寫「Code in this repository is licensed under Apache 2.0」，文件則採用 CC-BY-4.0。所以「Apache 2.0」只對了一半。https://github.com/agentskills/agentskills（約 2.7 萬星）
- 後續發展：2026-10-22，Anthropic 把 Agent Skills（名稱、logo、GitHub 組織和網域）捐給 AAIF。AAIF 專案頁已把它列入。https://aaif.io/projects/

### D. AGENTS.md / MCP / A2A 治理 — 已驗證（A2A 需要補充）

- Linux Foundation 新聞稿（2025-12-09）列出 AAIF 的創始專案：「Anthropic's Model Context Protocol (MCP), Block's goose, and OpenAI's AGENTS.md」 ✔ https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
- A2A：Google 在 2025-06-23 把它捐給 Linux Foundation，成立 Agent2Agent Project ✔。https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/
- 目前 AAIF 專案頁也列出 Agent2Agent (A2A)。二手來源說它在 2026-08 併入 AAIF，日期未經一手確認。

### E. 「>35% 公開 Skills 有安全缺陷，13% 含 prompt injection 或惡意程式」 — 大致驗證（出處是 Snyk ToxicSkills）

- Snyk 在 2026-02-05 掃描了 ClawHub 和 skills.sh 上的 3,984 個 skill。原文：「36.82% (1,467 skills) have at least one security flaw」，以及「13.4% … contain at least one critical-level security issue」。https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub
- 報告的說法有一處偏差：13.4% 是「critical 級問題」，包含惡意程式、prompt injection **和外洩的密鑰**，並非全都是注入或惡意程式。在完整 ClawHub 樣本中，prompt injection 只佔約 2.6%。
- 另一份學術研究（arXiv 2601.10338）分析了 31,132 個 skill，發現 26.1% 至少有一個漏洞。兩份研究的方法不同，不能混著引用。

### F. IBM 合規報表行列加總不符、改用確定性腳本 — 查無來源

- 用多組關鍵字搜尋 IBM Think、IBM Bob、watsonx 相關內容，都找不到這個案例。
- 「數字交給腳本、判斷交給 LLM」是常見原則，Red Hat 和 Umbraco 都寫過，但找不到 IBM 的具體案例。在找到原始出處之前，應視為未證實的軼事。

### G. 「Depot Cloud」當成 agent 用的拋棄式沙盒 — 大致驗證（產品名稱不精確）

- Depot 推出了「remote agent sandboxes」，`depot claude` 預設在遠端的隔離沙盒中執行。現在已改名為 **Managed Agents** 和 **Depot Sandboxes**（目前只支援 Linux）。https://depot.dev/blog/now-available-remote-agent-sandboxes 、https://depot.dev/docs/agents/overview
- 「Depot Cloud」不是正式產品名。

### H. 語意／情節／程序記憶對應到 RAG／memory／skills — 起源不是 Anthropic

- 把 agent 記憶分成 semantic / episodic / procedural，學術上的源頭是 **CoALA**（Sumers、Yao、Narasimhan、Griffiths，2023，Princeton）。https://arxiv.org/abs/2309.02427
- 這三類又源自認知科學（Tulving 等人的分類）。
- 「procedural = skills、semantic = RAG、episodic = 對話紀錄」是社群和 LangChain（LangMem）等延伸出來的普及說法，沒有單一發明者。
- 「RAG = semantic」也有人反對，認為 RAG 只是一種取用機制，不算一種記憶。
- 這次沒找到 Anthropic 官方提出這個對應的一手來源。

### I. Claude 模型名稱 — 已驗證（三個都存在，但都已不是最新）

- Anthropic 官方模型頁把 **Claude Opus 5、Claude Sonnet 5、Claude Haiku 4.5** 都列為「Legacy models (still available)」 ✔ https://platform.claude.com/docs/en/about-claude/models/overview
- 截至 2026-11 的現行模型是 Claude Fable 5.1、Opus 5.5、Sonnet 5.5 和 Haiku 5.5。
- 如果報告把 Opus 5 當成「現行最新」，就已經過時。

## 二、2026 主流 AI coding 工作流／方法論

| 名稱 | 是什麼 | Repo / URL | 熱度（GitHub 星） | 核心機制 |
|---|---|---|---|---|
| Superpowers | Jesse Vincent 的 skills 框架和開發方法論 | github.com/obra/superpowers | ~312k | brainstorm → 寫計畫 → 子代理逐任務實作 + TDD + 兩階段 review，skill 自動觸發 |
| Matt Pocock skills | 個人 skills 集（grill-me、grill-with-docs、tdd、to-prd、handoff…） | github.com/mattpocock/skills | ~312k | 先「拷問」釐清需求，產出術語表和 ADR，再交給 agent 實作 |
| gstack | Garry Tan 的 Claude Code 設定，23 個角色化工具 | github.com/garrytan/gstack | ~139k | 用 slash command 扮演 CEO、設計、工程、QA、發佈等角色，依序審查 |
| GitHub Spec Kit | GitHub 官方的 SDD 工具包 | github.com/github/spec-kit | ~147k | constitution → /specify → /plan → /tasks → /implement |
| Addy Osmani agent-skills | 「生產級」工程 skills 集 | github.com/addyosmani/agent-skills | ~113k | 依開發生命週期分段的 skills（spec、測試、review、上線） |
| Ruflo（原 claude-flow） | ruvnet 的多代理 swarm 編排 | github.com/ruvnet/ruflo | ~81k | 由 queen/worker 組成的 swarm，加上共享記憶和 MCP 工具 |
| OpenSpec | Fission-AI 的輕量 SDD | github.com/Fission-AI/OpenSpec | ~74k | 每次改動是一個 change proposal（proposal/tasks/spec delta），完成後歸檔併入主 spec，適合既有專案 |
| GSD (Get Shit Done) | 輕量的 meta-prompting 和 context 工程 | github.com/gsd-build/get-shit-done | ~64k（最後 push 是 2026-05） | 把專案狀態寫成 PROJECT/ROADMAP/STATE 文件，每個任務開新的 context 子代理，避免 context rot |
| BMAD Method | 敏捷式多角色 AI 開發方法 | github.com/bmad-code-org/BMAD-METHOD | ~55k | 用 Analyst、PM、Architect、SM、Dev、QA 等 persona 串成文件鏈，story 檔承載上下文 |
| wshobson/agents | 跨 harness 的 agents 和 plugins 市集 | github.com/wshobson/agents | ~42k | 大量專職子代理和 plugin，按需安裝 |
| Taskmaster | AI 任務管理（PRD → 任務樹） | github.com/eyaltoledano/claude-task-master | ~28k（最後 push 是 2026-04） | 解析 PRD 產生帶相依關係和複雜度分數的 tasks.json，透過 MCP 讓 agent 逐一領取 |
| Compound Engineering | Every 的官方 plugin | github.com/EveryInc/compound-engineering-plugin | ~26k | Plan → Work → Review → **Compound**，每輪把學到的東西寫回規則和 skill，讓之後越做越快 |
| SuperClaude | Claude Code 設定框架 | github.com/SuperClaude-Org/SuperClaude_Framework | ~24k | 提供指令、persona 和行為模式 flag |
| Ralph loop | Geoffrey Huntley 提出的「同一個 prompt 無限迴圈」 | ghuntley.com/ralph；github.com/snarktank/ralph（~22k）；frankbria/ralph-claude-code（~9.7k） | 見左欄 | `while true` 反覆餵同一份 PRD 或 prompt，靠檔案和 git 保存進度，直到所有項目完成 |
| HumanLayer / RPI | Dex Horthy 的「Advanced Context Engineering」 | github.com/humanlayer/humanlayer | ~13k | Research → Plan → Implement 三段，每段刻意壓縮 context（frequent intentional compaction） |
| Kiro specs | AWS 的 agentic IDE | kiro.dev；github.com/kirodotdev/Kiro（~4k，只放 issue） | 產品，看星數不準 | `.kiro/specs/` 底下有 requirements.md（EARS 格式）、design.md、tasks.md，加上 steering 和 hooks |
| Claude Code plan mode | 內建的唯讀規劃模式 | code.claude.com/docs | 內建 | Shift+Tab 進入，只讀不寫，產出計畫等使用者核准後才動手 |
| pstack | Cursor 的 Lauren Tan 的個人 skills | 收錄在 Cursor plugins；鏡像在 github.com/backnotprop/pstack | 只有移植版的星數 | 除錯 playbook 加多模型流程，刻意不做規劃，交給 plan mode |
| AGENTS.md | 跨工具的 repo 指令檔標準 | agents.md（AAIF） | 業界標準 | 在 repo 根目錄放一份給所有 agent 共用的說明 |
| Orca | Stably AI 的 ADE（agent 開發環境） | onorca.dev；github.com/stablyai/orca | — | 多個 CLI agent 各自在 git worktree 中平行執行；orca-cli skill 讓 agent 操控 Orca |

觀察：

- 2026 的主流可以分成幾條路線：
  - **規格驅動**：Spec Kit、OpenSpec、Kiro、BMAD
  - **技能框架**：Superpowers、Pocock、Osmani、gstack、pstack
  - **context 工程與迴圈**：GSD、RPI、Ralph
  - **複利學習**：Compound Engineering
- 星數最高的兩個是 Superpowers 和 Pocock skills，兩者都超過 31 萬。

## 未查證／風險

- The Gray Cat 影片本身（逐字稿和畫面）沒有看，所以 156 分鐘、$96.01、$94.05、236 和 861 行、Orca 這幾項只能標為「未在說明欄出現」，不能判定是錯的。
- IBM 案例找不到出處，不代表一定不存在。
- 星數是 2026-11-04 的單點快照。
