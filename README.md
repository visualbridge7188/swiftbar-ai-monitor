# 🚀 SwiftBar AI Status Monitor

[English](README.md) | [한국어](README_KR.md)

---

A lightweight, native macOS menu bar plugin for [SwiftBar](https://github.com/swiftbar/SwiftBar) that monitors token usage, rate limits, and reset times for **Codex**, **Antigravity**, and **Z AI**.

---

## 🔍 Features

1. **🎨 High-Res Progress Bar Graphics (Pillow)**
   * Renders sleek progress bar images dynamically in memory (RAM) using Pillow (PIL), avoiding ASCII character wrappers.
   * Leverages transparent tracks and adaptive styling to look premium on both light and dark macOS menu bars.

2. **⏱️ 7-Day Token Pacing Logic (Pacing & Expected Line)**
   * Evaluates if your current token consumption is appropriate relative to the remaining time of the 7-day rate window.
   * Draws a vertical pacing tick (budget line) on the gauge. The marker turns **red** if you are over budget (over-using) and **green** if you are on track.

3. **🤖 Antigravity Local Language Server Probing**
   * Automatically discovers the running local Antigravity process (`ps`) and listening ports (`lsof`).
   * Extracts the local security token (`--csrf_token`) and connects directly to the local Connect RPC backend API.
   * Groups and segments your quotas by model family, displaying separate progress indicators for **Claude**, **Gemini Pro**, and **Gemini Flash** (filtering lite, autocomplete, or image models).
   * Supports seamless fallback to the command line utility (`antigravity-usage`) or mock/simulated quotas if the local language server is offline.

4. **⚡ Z AI Dual Limits**
   * Monitors both MCP call quotas (`TIME_LIMIT`) and model token limits (`TOKENS_LIMIT`) simultaneously.

---

## 📂 Project Structure

```text
├── README.md               # Project documentation
├── ai_status.5m.py         # Main SwiftBar plugin script (runs every 5 minutes)
├── .config.json            # Hidden config file for API keys
├── docs/                   # Design specifications and documentation
└── tests/                  # Automated unit test suite
```

---

## ⚙️ Requirements & Setup

### 1. Requirements
* **macOS** with [SwiftBar](https://github.com/swiftbar/SwiftBar) installed.
* **Python 3** (Homebrew python recommended) with **Pillow** installed.
  ```bash
  pip3 install pillow
  ```

### 2. Installation
1. Copy [ai_status.5m.py](ai_status.5m.py) to your SwiftBar plugins directory.
2. Ensure the script is executable:
   ```bash
   chmod +x ai_status.5m.py
   ```
3. Open or create `.config.json` in your plugins folder to configure your Z AI API key:
   ```json
   {
       "Z_AI_API_KEY": "your-z-ai-api-key"
   }
   ```
4. Refresh SwiftBar using the menu items or run:
   ```bash
   open -g "swiftbar://refreshAll"
   ```

---

## 🧪 Running Tests

You can run the full automated unit test suite to verify code correctness and mock data handling:

```bash
python3 -m unittest discover -s tests -v
```

Expected output:
```text
test_get_antigravity_cli_fallback (test_cli_fetch.TestCliFetch) ... ok
test_get_antigravity_local_success (test_cli_fetch.TestCliFetch) ... ok
test_get_codex (test_cli_fetch.TestCliFetch) ... ok
test_config_generation (test_config.TestConfig) ... ok
test_get_zai (test_http_fetch.TestHttpFetch) ... ok
test_render_output (test_ui_render.TestUIRender) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.012s

OK
```

---

## 📄 License

This project is licensed under the MIT License.