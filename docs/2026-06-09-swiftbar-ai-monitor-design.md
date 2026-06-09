# SwiftBar AI Tools Token Monitor Design Spec

## 1. Overview
A lightweight, native macOS menu bar plugin for SwiftBar that monitors token balances and reset times for Codex, Antigravity, and Z AI. It updates automatically every 5 minutes and supports manual forced refresh with visual preloader feedback.

## 2. Architecture & Data Flow
- **Environment**: Python 3 (built-in macOS), executed by SwiftBar.
- **Filename**: `ai_status.5m.py` (The `.5m` suffix tells SwiftBar to run it every 5 minutes).
- **Configuration**: `config.json` file located in the same directory. Stores the Z AI API key. The script will automatically generate a dummy `config.json` if it does not exist.
- **External Dependencies**: None. Uses only standard library modules (`subprocess`, `urllib.request`, `json`, `sys`, `os`).

### Data Sources
1. **Codex**: 
   - Command: `subprocess.run(["codex", "status", "--json"])`
   - Data points: `tokens_remaining`, `reset_in_seconds`
2. **Antigravity**: 
   - Command: `subprocess.run(["antigravity-usage", "--status", "json"])`
   - Data points: `model_quota.gemini-pro`, `next_reset_epoch`
3. **Z AI**: 
   - HTTP API via `urllib.request` to `https://api.z.ai/api/monitor/usage/quota/limit`
   - Auth: Bearer token from `config.json`
   - Data points: `remaining_requests`, `next_reset_time`

## 3. UI/UX Design (Menu Bar & Dropdown)

### Main Menu Bar Display
Displays the compact status of all three tools:
`🤖 CX: {Codex} | 🚀 AG: {Antigravity} | ⚡️ Z: {Z_AI}`
- **Alert System**: If any tool's quota falls below a defined threshold (e.g., 10%), that specific segment's text color changes to red (`color=red` in SwiftBar format) to alert the user.

### Dropdown Details
Displays human-readable detailed stats and reset times.
```
🤖 Codex: 45k (Reset in 12m)
---
🚀 Antigravity: 82% (Reset in 1h 5m)
---
⚡️ Z AI: 85 (Next Reset: 18:00)
---
🔄 Force Refresh Data | refresh=true
```
- **Manual Refresh**: Clicking `Force Refresh Data` triggers SwiftBar's native `refresh=true` action, which immediately re-executes the script. SwiftBar natively displays a spinning preloader (loading indicator) in the menu bar while the script is running.

## 4. Error Handling & Resilience
- **Isolated Execution**: Data fetching for each of the three services is wrapped in its own `try-except` block.
- **Partial Failure**: If one service fails (e.g., Z AI API is down or CLI tool is unauthenticated), it does not crash the entire plugin. The failed service will display `⚠️ Error` on the menu bar, while the other services continue to show valid data.
- **Debug Logs**: The specific exception error message for the failed service will be printed inside the dropdown menu for easy debugging.
