---
tier: T2
status: done
components: [skills]
evidence:
  - skills/oss-release-readiness/scripts/release_check.py:34
  - skills/oss-release-readiness/scripts/release_check.py:111
verified_by:
  - C:/Python313/python.exe -I tests/test_release_check.py
reviewed_by: [fresh-context subagent]
supersedes: []
---
## 為什麼
skill-lab 要公開，公開前要能檢查 HEAD 和全部歷史有沒有不能公開的內容。

## 行為改變
新增 `oss-release-readiness` skill 和 `scripts/release_check.py`：檢查被禁止字串（HEAD 內容含二進位、歷史、提交訊息、作者信箱、annotated tag 的訊息與 tagger、HEAD 與歷史的檔名）、敏感路徑、notebook 輸出、超過 5 MiB 的檔案、缺少的 LICENSE/README.md/SECURITY.md、第三方 skill 的出處。發現不會印出被禁止字串本身。`ARCHITECTURE.md` 的 `skills` behavior 已更新，`evals/routing.json` 加了一案（結果待量，Task 5）。

## 決策（含 Rulings）
- 只用標準函式庫，用 `git grep` 和 `git log --all -S` 檢查；`-S` 與值相連、`-e` 與 `--` 避免以 `-` 開頭的值被當成選項。
- `git grep` 結束碼 1 是沒有命中，不是錯誤；有 ref 但沒有 HEAD 的 repo，`main` 回 2 並說明。
- 路徑本身含被禁止字串時，輸出以 `<forbid[n]>` 取代。
- git 失敗、空的或含換行的 `--forbid` 都回 2，不會和發現混淆；從子目錄執行會先找 toplevel。
- 無法解析的 notebook 報 `notebook-unreadable`；nbformat 3 的 worksheets 也算；submodule 大小 `-` 當 0；敏感路徑不分大小寫，含 `.env.*`。
- 所有被禁止字串在同一次比對中取代，長的優先。
- SKILL.md 補 `--replace-message` 和 Windows 路徑各種寫法。
- 改寫歷史由擁有者在自己的終端機執行，因為 hook 會擋。

## 沒做／已知限制
- 進行中（partial）：尚未審查；路由案例還沒跑（Task 5）。
- HEAD 的二進位檔也會比對（回報 `binary`）；編碼或混淆過的秘密找不到。
- 作者和提交者只檢查信箱，不檢查名字。
- 檔名比對是整個路徑的子字串；敏感路徑則看 basename。
- bare 或 mirror clone 回 2；巢狀在別的 repo 內的目錄會掃外層 repo。
