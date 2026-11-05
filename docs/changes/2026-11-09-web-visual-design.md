---
tier: T2
status: partial
components: [skills]
evidence:
  - skills/web-visual-design/scripts/palette_check.py:53
  - skills/web-visual-design/scripts/palette_check.py:87
verified_by:
  - C:/Python313/python.exe -I tests/test_palette_check.py
reviewed_by: []
supersedes: []
---
## 為什麼
擁有者接受美術風險的條件：先建立可驗證的網站視覺設計 skill。依 writing-skills 先量沒有 skill 的基準，再寫 skill。

## 行為改變

## 決策（含 Rulings）
- `check()` 的對比數字用截斷而非四捨五入顯示，4.499 不會被顯示成 4.50。
- 色彩的通過門檻只用 WCAG 2.2；APCA 只當輔助，只能往上加對比，不能低於 WCAG。WCAG 3 工作草案（2026-09-10）寫明演算法未定。
- `text-autospace` 要明確寫 `normal`：規格和 CSSWG 決議（2025-12-10）的初始值是 `normal`，但瀏覽器相容性資料記載已發佈版本的初始值是 `no-autospace`。
- 中文每行字數和行距採 clreq §7.1.1.5 的書籍數字（17 到 40 字；行距 50% 到 100%），並標明只適用書籍；網頁沒有權威數字，其餘標 working default。
- `palette_check` 不動。空的 `pairs` 會通過，所以 SKILL.md 要求列出每個用到的配對，並要求按鈕文字標 `body`。
- Material 3 查不到內容，不採用。

## 沒做／已知限制
- 進行中（partial）：已有 `palette_check.py`、其測試、評測檔，以及 `SKILL.md` 和 `references/`。
- 尚未部署，也還沒做 GREEN 量測、路由案例和 `ARCHITECTURE.md` 更新（Steps 10 到 12）。
- `pyftsubset` 指令取自文件，本機沒裝 fontTools，沒有實際跑過。
- 中文字型組合的 `unicode-range` 寫法是推導而來，沒有權威來源，也還沒在瀏覽器實測。
