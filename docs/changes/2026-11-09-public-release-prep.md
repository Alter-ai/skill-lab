---
tier: T2
status: partial
components: [skilllab, audit, gate, skills]
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
- 更正：`2026-11-09-oss-release-readiness.md` 與 `2026-11-09-web-visual-design.md` 的「沒做／已知限制」寫著 partial、路由案例尚未跑；實際上兩者都已 done、路由也跑過（結果見上）。done 紀錄不改，以本段為準。
- Ruling: T3 eval arms are dispatched by the controller, not the implementer — implementers may not spawn subagents — no cost beyond controller context.
- Ruling: each T2 task commits status: partial; after the task review passes, a final commit sets status: done with reviewed_by — the gate requires a reviewer dispatch containing the change path after the file first appears — if wrong, the gate blocks and tells us.
- Ruling: branch in place, no worktree — plan's Global Constraints name the repo checkout on this branch, and the gate hook lives in that checkout — cost if wrong: dirty-tree risk only.
- Ruling: Task 1 run by the controller, no review — no repo change — none.
- Ruling: gh auth deferred to the owner before Task 6; T5 looks up action SHAs via the unauthenticated GitHub REST API — needs no credentials — rate limit only.
- Ruling: gate-evidence test runs and the status: done commit happen in the controller session from the repo cwd — subagent test runs are not recorded in the gate's evidence log, which is the documented requirement rather than a bypass — cost: slightly more controller context.
- Ruling: T3 split: part A (steps 1-5, script and eval file) sonnet; controller runs baseline (step 6); part B (steps 7-9, knowledge) on opus; controller runs with-skill arm and blind review (step 10) — implementers may not dispatch subagents, knowledge writing needs most judgment — cost: two implementers.
- Ruling: palette_check rejects empty or missing pairs, beyond plan's listed tests — otherwise the rubric color item passes vacuously — cost: none.
- Ruling: run one quality round despite the formal pass — reviewer found template convergence, overlength, and technical errors that undercut the owner's condition of real design knowledge — cost: one fix dispatch and one re-measure.
- Ruling: stop after a small guidance edit, no third measured round — the pass condition is met twice, the owner chooses among three directions in S2 which reduces the harm, and usage is limited — cost: the edit is unmeasured and convergence stays a stated limitation.
- Ruling: Task 6 must also pass --replace-message to git filter-repo — replace-text does not rewrite commit messages, a plan omission found by review — cost: none.
- Ruling: Task 5 routing regression reduced to the two new cases x3 plus one non-tier case per area x1, on headless sonnet with a turn cap, not all 35 — the owner hit the usage limit once today and a full run is costly — cost: a routing regression could go unseen; stated in the results and final message.
- Ruling: Task 5's change stays status: partial until the final review, so final fixes land in it rather than editing a done record — done changes are history under change-record — cost: none.
- Ruling: change one condition in tools/gate.py and its tests — the owner's rule forbids editing gate files when blocked in order to bypass; this is a bug fix found in review, not a response to a block, and does not weaken the gate — cost: if the owner disagrees, revert one commit and keep CI Windows-only.
- Ruling: Task 6 plan updated with pyc removal, identifier rules, per-spelling verification and master checkout, and dry-run in a temp clone before handing over — publication is irreversible — cost: none.

## 沒做／已知限制
- 進行中（partial）：尚未審查。
- 快速開始的 `CLAUDE_CODE_CHILD_SESSION=1 git commit` 無法在 Claude session 內字面執行（pretool hook 擋下改動該變數的指令）；改在 session 內直接 `git commit`，因為該變數已設，得到同樣的 `gate: blocked`。
- CI 在 Ubuntu 上的結果未驗證；測試只在 Windows 跑過。
- Scorecard 估計依官方 docs/checks.md（20 項）；Packaging、Signed-Releases、Webhooks 無物可查時的計分方式官方頁面沒寫，估計中按保守假設處理。
