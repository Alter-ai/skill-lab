# Hook payload spike（2026-11-04，Claude Code 桌面版，Windows 11）

做法：在 `~/.claude/settings.json` 暫時加入 `PostToolUse` 和 `PostToolUseFailure` 兩個 hook，matcher 為 `Bash|PowerShell|Agent`，把收到的 stdin 原樣寫進檔案。接著依序執行一次成功的 Bash、一次失敗的 Bash、一次 PowerShell，再派一個 Agent。觀察完已移除這兩個 hook。

## 觀察結果

| 項目 | 實測 |
|---|---|
| 環境變數 | Bash 與 PowerShell 工具中，`CLAUDE_CODE_CHILD_SESSION` 和 `CLAUDECODE` 都是 `1` |
| Bash 成功 | 觸發 `PostToolUse`，`tool_name: "Bash"`，`tool_input` 含 `command`、`description`；`tool_response` 含 `stdout`、`stderr`、`interrupted`、`isImage`、`noOutputExpected`，**沒有 exit code** |
| Bash 失敗（exit 3） | 觸發 `PostToolUseFailure`，`error: "Exit code 3"`；有 `is_interrupt`，沒有 `tool_response` |
| PowerShell | `tool_name: "PowerShell"`，欄位和 Bash 相同（沒有 `noOutputExpected`） |
| 子代理 | `tool_name: "Agent"`，`tool_input` 含 `prompt`、`description`、`subagent_type`、`model`。背景派發時，`PostToolUse` 在**啟動當下**就觸發（`tool_response.status: "async_launched"`），不是等子代理完成才觸發 |
| `cwd` | Windows 格式的反斜線路徑，例如 `<home>\code\skill-lab-gate`。它是 **session 的工作目錄**，不是指令裡 `cd` 之後的目錄 |
| 共通欄位 | `session_id`、`transcript_path`、`permission_mode`、`prompt_id`、`duration_ms`。主 session 的事件沒有 `agent_id` |

## 對計畫的影響

- Task 4：
  - Agent 工具名稱確定是 `Agent`，prompt 從 `tool_input.prompt` 取得。
  - 判斷成功或失敗只看事件名稱；`PostToolUseFailure` 一律記為 `ok:false`。
  - 用 `cwd` 找 repo 時，要先把反斜線換成正斜線。
- 已知限制：像 `cd other-repo && pytest` 這類指令，會被記到 session `cwd` 所在的 repo。gate 只比對內容 hash，記錯 repo 頂多是少一筆證據，結果會被擋下，不會被誤放行。
- Task 10：`PostToolUse` 和 `PostToolUseFailure` 的 matcher 用 `Bash|PowerShell|Agent`。
