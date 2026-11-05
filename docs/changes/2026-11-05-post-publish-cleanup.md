---
tier: T2
status: partial
components: [skilllab]
evidence:
  - .github/workflows/test.yml:27
verified_by:
  - C:/Python313/python.exe -I tests/test_skill_audit.py
reviewed_by: []
supersedes: []
---
## 為什麼
公開後的收尾：CI 在 Ubuntu 已通過，文件要更新；安全審查建議鎖定 CI 相依版本，並補齊來源紀錄。

## 行為改變

## 決策（含 Rulings）
- Dependabot 的兩個更新在本機以 noreply 身分合併，不用網頁合併，避免作者信箱寫入公開歷史。
- `matplotlib` 只鎖版本，未鎖雜湊。CI 沒有機密且權限唯讀，這樣已足夠。

## 沒做／已知限制
- macOS 仍未測試。
