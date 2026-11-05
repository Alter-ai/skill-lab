---
tier: T2
status: partial
components: [skills]
evidence:
  - skills/webapp-testing/scripts/with_server.py:1
verified_by:
  - C:/Python313/python.exe -I tests/test_skill_audit.py
  - "manual: C:/Python313/python.exe -I tools/skill_audit.py local=skills 結果 17 skills, 0 flagged, 無 30% 以上重疊"
reviewed_by: []
supersedes: []
---
## 為什麼
公開釋出前，補齊前端設計、前端工程、網頁測試、安全加固和效能優化五個第三方 skill，讓 repo 自成一套。

## 行為改變
`skills/` 新增五個 skill：`frontend-design`、`webapp-testing`（anthropics/skills，Apache-2.0，commit ca45fc496a3436251f191354091d557da31c15b5）和 `security-and-hardening`、`frontend-ui-engineering`、`performance-optimization`（addyosmani/agent-skills，MIT，commit 301b02b12bff98e4688e6984af6556802322bbde）。每個都有 `LICENSE` 與 `SOURCE.md`。`webapp-testing` 帶有 `scripts/with_server.py`。`ARCHITECTURE.md` 的 `skills` 元件 `behavior` 加入來源紀錄規則。

## 決策（含 Rulings）
- 只引入這五個；上游其他 skill 不碰。
- 指向未引入檔案或 skill 的段落（`../../references/*-checklist.md`、`observability-and-instrumentation`、`debugging-and-error-recovery`）最小幅度改寫或刪除，逐條記在各 `SOURCE.md` 的 `Local modifications`。
- Anthropic 的 `LICENSE.txt` 改名為 `LICENSE`，frontmatter 的 `license` 欄同步。
- 上游 `references/` 子目錄（security、performance）隨 SKILL.md 一起複製，因為 SKILL.md 直接連結它們。

## 沒做／已知限制
- `skill_audit` 無 30% 以上重疊，無需記錄。
- `webapp-testing/examples/` 仍寫入上游沙盒路徑 `/mnt/user-data/outputs/`，在這台機器上要先改路徑才能跑；未改動。
- 沒有引入上游 `references/*-checklist.md`，相關檢查清單內容缺席。
- 尚未經 fresh-context reviewer 審查（status 維持 partial）。
