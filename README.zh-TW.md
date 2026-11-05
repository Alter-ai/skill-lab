# skill-lab

[English](README.md) | 繁體中文

個人用的 [Claude Code](https://claude.com/claude-code) skills，加上建立和檢查它們的小工具：一個要求 AI 工作階段宣告改動風險等級的 commit gate、一個 `SKILL.md` 檢查器，和一組路由測試案例。

## 解決什麼問題

AI 寫程式時容易走最短路徑：跳過規格、測試和審查。只靠提示詞裡的指示，只能讓好行為「比較可能」出現。這個 repo 想把關鍵步驟變成可檢查的：

- **Tier gate**（`tools/gate.py`）：`commit-msg` hook。Claude Code 工作階段提交時，訊息必須有 `Tier: T0..T3`；T2/T3 還要指向 `docs/changes/` 裡一份符合 `change-record` skill 規則的 change file，否則 commit 被擋下。
- **Skill audit**（`tools/skill_audit.py`）：靜態檢查 `SKILL.md` 的大小、frontmatter 限制、失效的引用，以及 skill 之間的內文重複。
- **路由案例**（`evals/routing.json`）：提示詞、預期載入的 skill 或行為，和實際觀察到的結果，讓修改 skill 描述前後可以和基準比對。

## 快速開始（約五分鐘）

需要 Python 3.13 和 git。在 Linux 或 macOS 上若指令名稱是 `python3`，請以 `python3` 取代 `python`。

```bash
git clone https://github.com/Alter-ai/skill-lab
cd skill-lab
python -I tests/test_skill_audit.py          # 印出 ok
python -I tools/skill_audit.py local=skills  # 檢查本 repo 的 skills
```

在一個用完即丟的 repo 試 gate（快速開始是 bash 語法；Windows 請用 Git Bash）：

```bash
cd ..                                        # 離開 skill-lab；demo repo 與它同層
mkdir demo && cd demo && git init
git config user.name you && git config user.email you@example.com   # git 提交需要身分
echo 'test_commands = []' > .agent-gate     # 有這個檔案，這個 repo 才啟用 gate
echo hi > a.txt && git add .
python ../skill-lab/tools/gate.py install   # 安裝 .git/hooks/commit-msg
CLAUDE_CODE_CHILD_SESSION=1 git commit -m "x"
```

預期輸出：

```
gate: blocked (see skill change-record)
missing 'Tier: T0|T1|T2|T3' trailer in commit message
```

hook 只在 `CLAUDE_CODE_CHILD_SESSION=1` 時作用。作者實測（Windows 11 的 Claude Code 桌面版，見 `docs/changes/2026-11-04-hook-payload-spike.md`）Bash 與 PowerShell 工具中有設定此變數；其他版本與平台未驗證。你在一般終端機直接 `git commit` 不受檢查。

要使用 skills，把需要的目錄從 `skills/` 複製到 `~/.claude/skills/`。`examples/CLAUDE.md` 是作者使用的使用者層規則檔（Tier 表和 skill 路由），使用前請自行調整。

## 內容清單

本 repo 自己寫的部分（MIT）：

| 路徑 | 內容 |
|---|---|
| `skills/change-record` | change file 範本和 gate 的規則 |
| `skills/backlog` | 單人 Scrum backlog，附甘特圖腳本 |
| `skills/web-visual-design` | 配色、中英混排字體和版面層次，附 WCAG 對比檢查 `palette_check.py` |
| `skills/oss-release-readiness` | 公開前檢查 HEAD 和全部歷史，附 `release_check.py` |
| `tools/` | `gate.py`、`skill_audit.py` |
| `evals/` | 路由案例和評估結果 |
| `examples/CLAUDE.md` | 使用者層規則檔（Tier 表和 skill 路由） |
| `tests/` | 每個檔案各自檢查，通過時印出 `ok` |
| `docs/` | 架構、變更紀錄、研究筆記 |

從其他專案匯入的部分。各目錄保留自己的 `LICENSE`，並用 `SOURCE.md` 記錄上游 commit：

| Skill | 上游 | 授權 |
|---|---|---|
| api-and-interface-design、ci-cd-and-automation、documentation-and-adrs、frontend-ui-engineering、git-workflow-and-versioning、performance-optimization、security-and-hardening、shipping-and-launch | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | MIT |
| c4-architecture | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) | MIT |
| frontend-design、webapp-testing | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 |
| competitive-brief、synthesize-research、user-research、ux-copy | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Apache-2.0 |

根目錄的 `LICENSE` 只涵蓋作者自己寫的部分，上表的目錄各依自己的授權。

## AI 參與方式

這個 repo 大部分由 Claude Code 在作者指示下寫成，用的就是 repo 所描述的工作流程。作者訂定目標和規則、閱讀並決定設計、執行這些工具。測試也由 AI 撰寫。gate 啟用之後，T2 和 T3 的改動都有 `docs/changes/` 的 change file，且多數經過 fresh-context 的 AI 審查；更早的 commit 沒有，也不是每個 commit 都有 `Tier:` trailer。沒有對每一行做過獨立的人工審查，請當作未經審計的個人工具使用。

## 已知限制

- 只在 Windows 11、Python 3.13 開發和測試。CI 也設定在 Ubuntu 上執行，但尚未確認結果；Linux 和 macOS 的使用經驗較少。
- gate 只作用於 Claude Code 工作階段，擋不了人。`gate.py` 還有 `pretool` 和 `evidence` 子命令，設計成 Claude Code hook 使用（用來擋繞過 commit hook 的嘗試）；快速開始沒有設定它們，在 `settings.json` 接上需要手動操作。
- `tests/test_render.sh` 需要 mermaid-cli，CI 不跑。`tests/test_gantt.py` 需要 `matplotlib`。
- `web-visual-design` 的評估只用 3 份 brief、由 AI 審查，沒有實際渲染，也沒有人看過結果；見 [evals/results/2026-11-web-visual-design.md](evals/results/2026-11-web-visual-design.md)。
- 路由結果來自小樣本的 headless 執行，不是統計研究。

## 貢獻與安全

見 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [SECURITY.md](SECURITY.md)。聯絡：lericai0705@gmail.com。
