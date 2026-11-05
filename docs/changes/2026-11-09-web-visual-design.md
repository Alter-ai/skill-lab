---
tier: T2
status: partial
components: [skills]
evidence:
  - skills/web-visual-design/scripts/palette_check.py:55
  - skills/web-visual-design/scripts/palette_check.py:98
verified_by:
  - C:/Python313/python.exe -I tests/test_palette_check.py
reviewed_by: []
supersedes: []
---
## 為什麼
擁有者接受美術風險的條件：先建立可驗證的網站視覺設計 skill。依 writing-skills 先量沒有 skill 的基準，再寫 skill。

## 行為改變
新增 `web-visual-design` skill（SKILL.md、references、`scripts/palette_check.py`）。`palette_check` 檢查 tokens 的 WCAG 2.2 對比，空的 `pairs` 和格式錯誤都回報為問題，不會丟 traceback。`ARCHITECTURE.md` 的 `skills` behavior 已更新，`evals/routing.json` 加了一案（結果待量）。

## 決策（含 Rulings）
- `check()` 的對比數字用截斷而非四捨五入顯示，4.499 不會被顯示成 4.50。
- 色彩的通過門檻只用 WCAG 2.2；APCA 只當輔助，只能往上加對比，不能低於 WCAG。WCAG 3 工作草案（2026-09-10）寫明演算法未定。
- `text-autospace` 要明確寫 `normal`：規格和 CSSWG 決議（2025-12-10）的初始值是 `normal`，但瀏覽器相容性資料記載已發佈版本的初始值是 `no-autospace`。
- 中文每行字數和行距採 clreq §7.1.1.5 的書籍數字（17 到 40 字；行距 50% 到 100%），並標明只適用書籍；網頁沒有權威數字，其餘標 working default。
- 空的 `pairs` 不會通過；只列部分配對仍會通過，所以 SKILL.md 要求全部列出，按鈕文字標 `body`，有意義的邊框和焦點環要有具名 token。
- 中文的 large 字級 WCAG 只說要等效，沒有具體數字，也查不到中文數值，所以中文一律用 `body`（4.5）。
- 第一輪盲測顯示 skill 造成範本收斂和超長。改成三個明顯不同的色票範例，不給固定數值；規格本體遵守 brief 的長度，推導和自我檢查放附錄；新增物件規則步驟。
- 字型堆疊和 `text-autospace` 的行為在 Chrome 152 實測過；`pyftsubset` 在本機 Noto Sans TC 上實跑過，`--layout-features='*'` 只增加體積，已移除。
- Material 3 查不到內容，不採用。

## 沒做／已知限制
- 進行中（partial）：已有 `palette_check.py`、其測試、評測檔，以及 `SKILL.md` 和 `references/`。
- 第二輪 GREEN 量測和結果檔尚未做；路由案例已加，但還沒跑（Task 5）。
- 字型堆疊的 `unicode-range` 寫法是推導而來，沒有權威來源，只在 Chrome 152 測過，Firefox 和 Safari 沒測。
- Noto Sans TC 子集是否要改名，要由人判斷；skill 裡寫的不是法律意見。
