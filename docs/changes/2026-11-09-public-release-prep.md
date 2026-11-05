---
tier: T2
status: partial
components: [skilllab, audit]
evidence:
  - tools/skill_audit.py:21
  - tests/test_skill_audit.py:50
verified_by:
  - C:/Python313/python.exe -I tests/test_skill_audit.py
  - C:/Python313/python.exe -I tests/test_palette_check.py
reviewed_by: []
supersedes: []
---
## 為什麼
skill-lab 要公開。工作樹要先乾淨（工具裡沒有本機路徑）、有授權和社群檔案、有 CI，並確認新加的兩個 skill 會被路由到。

## 行為改變
- `tools/skill_audit.py` 不再寫死本機路徑：沒有參數時只讀家目錄下 ponytail marketplace 的 skills，其他根目錄用 `prefix=dir` 傳入。
- 新增 `.github/workflows/test.yml`（push 和 pull_request，ubuntu 與 windows，actions 釘選 SHA）和 `.github/dependabot.yml`。
- 新增 README（英、繁中）、LICENSE（MIT）、SECURITY、CONTRIBUTING、`docs/scorecard-estimate.md`；`CLAUDE.md.draft` 改為 `examples/CLAUDE.md`（移除開頭註解）。
- `ARCHITECTURE.md` 的 `audit` behavior 和 `AGENTS.md` 已更新。

## 決策（含 Rulings）
- 路由回歸縮小範圍：只跑 `wvd-1`、`ossr-1` 各 3 次，加上每個非 tier 領域的第一案各 1 次，共 11 次（headless `claude -p`、`--model sonnet`、`--max-turns 3`、空的暫存目錄）。其餘 28 案沒有重跑，`expected` 未改。新案兩個都 3/3 載入自己的 skill。
- 非 tier 案和基準的差異都不涉及我們的 skill：c2-a 在空目錄載入了 systematic-debugging（基準沒載入任何 skill）；c3-a 沒有 PR 所以沒載入 ponytail-review；c5-a 只做 Glob。
- action SHA 用未登入的 REST API 查（`gh` 未登入）：checkout v4、setup-python v5。
- MIT、docs 公開、`examples/CLAUDE.md` 採預設值。個人字串留在舊 commit 和 docs 內，由 Task 6 處理。
- `tests/test_palette_check.py` 用 redirect 吃掉預期的錯誤輸出，通過時只印 `ok`。

## 沒做／已知限制
- 進行中（partial）：尚未審查。
- 快速開始的 `CLAUDE_CODE_CHILD_SESSION=1 git commit` 無法在 Claude session 內字面執行（pretool hook 擋下改動該變數的指令）；改在 session 內直接 `git commit`，因為該變數已設，得到同樣的 `gate: blocked`。
- CI 在 Ubuntu 上的結果未驗證；測試只在 Windows 跑過。
- Scorecard 的檢查清單和權重憑記憶寫成，未對照線上文件。
