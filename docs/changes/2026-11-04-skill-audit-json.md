---
tier: T2
status: done
components: [audit]
evidence:
  - tools/skill_audit.py:107
  - tests/test_skill_audit.py:42
verified_by:
  - C:/Python313/python.exe -I tests/test_skill_audit.py
reviewed_by: [fresh-context subagent]
supersedes: []
---
## 為什麼
第一次在 skill-lab 實際走一遍 tier gate 的完整流程（Task 10 的煙霧測試），同時讓 `skill_audit.py` 的結果能被其他工具或 AI 直接讀取，不必解析表格文字。

## 行為改變
`tools/skill_audit.py` 新增 `--json` 旗標：改為輸出 JSON（`skills`、`flagged`、`overlap`），exit code 規則不變（有任何 skill 被標記就回 1）。不帶 `--json` 時輸出與以前完全相同。`docs/architecture/ARCHITECTURE.md` 首次建立，`audit` 元件的 `behavior` 記錄了這個旗標。

## 決策（含 Rulings）
- JSON 的欄位直接沿用表格的欄位（`lines`、`bytes`、`name_len`、`desc_len`、`flags`），不另外設計 schema。
- 依 skill 名稱排序，讓輸出穩定可比對；表格模式維持原本依大小排序。

## 沒做／已知限制
- 沒有 schema 版本欄位；之後若改欄位，讀取端要自己處理。
- ARCHITECTURE.md 目前只到 Container 層，且只列出這次和 gate 有關的元件。
