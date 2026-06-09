# SwiftBar AI Monitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a native macOS SwiftBar plugin (Python script) to monitor Codex, Antigravity, and Z AI tokens with error handling and auto-refresh.

**Architecture:** A single Python script `ai_status.5m.py` executed by SwiftBar every 5 minutes. Uses standard libraries (`subprocess`, `urllib.request`, `json`) to fetch data. Generates and reads a `config.json` for API keys.

**Tech Stack:** Python 3 (macOS system Python), standard libraries.

---

### Task 1: Basic Structure and Config Management

**Files:**
- Create: `ai_status.5m.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
import unittest
import os
import json
import importlib.util

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a clean environment
        if os.path.exists('config.json'):
            os.remove('config.json')
            
    def test_config_generation(self):
        # Dynamically import the script to test its functions
        spec = importlib.util.spec_from_file_location("ai_status", "ai_status.5m.py")
        ai_status = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_status)
        
        config = ai_status.load_config()
        
        self.assertTrue(os.path.exists('config.json'))
        self.assertIn('Z_AI_API_KEY', config)
        self.assertEqual(config['Z_AI_API_KEY'], 'YOUR_API_KEY_HERE')

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_config.py -v`
Expected: FAIL with "No module named 'ai_status'" (file doesn't exist yet)

- [ ] **Step 3: Write minimal implementation**

```python
# ai_status.5m.py
#!/usr/bin/env python3
# <bitbar.title>AI Tools Total Monitor</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>User</bitbar.author>
# <bitbar.desc>Monitors Codex, Antigravity, and Z AI tokens natively</bitbar.desc>

import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "Z_AI_API_KEY": "YOUR_API_KEY_HERE"
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    config = load_config()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `chmod +x ai_status.5m.py && python3 -m unittest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ai_status.5m.py tests/test_config.py
git commit -m "feat: setup basic script structure and config auto-generation"
```

---

### Task 2: CLI Data Fetching (Codex & Antigravity)

**Files:**
- Modify: `ai_status.5m.py`
- Create: `tests/test_cli_fetch.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli_fetch.py
import unittest
from unittest.mock import patch, MagicMock
import importlib.util

spec = importlib.util.spec_from_file_location("ai_status", "ai_status.5m.py")
ai_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_status)

class TestCliFetch(unittest.TestCase):
    @patch('subprocess.run')
    def test_get_codex(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = '{"tokens_remaining": 45000, "reset_in_seconds": 720}'
        mock_run.return_value = mock_result
        
        result = ai_status.get_codex_data()
        self.assertEqual(result['remaining'], "45k")
        self.assertEqual(result['reset'], "12m 0s")
        self.assertFalse(result['alert'])

    @patch('subprocess.run')
    def test_get_antigravity(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = '{"model_quota": {"gemini-pro": "82%"}, "next_reset_epoch": 0}'
        mock_run.return_value = mock_result
        
        result = ai_status.get_antigravity_data()
        self.assertEqual(result['remaining'], "82%")
        self.assertFalse(result['alert'])

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_cli_fetch.py -v`
Expected: FAIL with "module has no attribute 'get_codex_data'"

- [ ] **Step 3: Write minimal implementation**

```python
# ai_status.5m.py (add after load_config)
import subprocess

def format_time(seconds):
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}m {secs}s"

def get_codex_data():
    try:
        result = subprocess.run(["codex", "status", "--json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        tokens = data.get("tokens_remaining", 0)
        reset_sec = data.get("reset_in_seconds", 0)
        
        # simple format: 45000 -> 45k
        formatted_tokens = f"{tokens // 1000}k" if tokens >= 1000 else str(tokens)
        alert = tokens < 5000 # Alert if less than 5k tokens
        
        return {
            "remaining": formatted_tokens,
            "reset": format_time(reset_sec),
            "alert": alert,
            "error": None
        }
    except Exception as e:
        return {"remaining": "?", "reset": "?", "alert": True, "error": str(e)}

def get_antigravity_data():
    try:
        result = subprocess.run(["antigravity-usage", "--status", "json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        quota = data.get("model_quota", {}).get("gemini-pro", "0%")
        
        # parse percent value for alert
        quota_val = int(quota.replace("%", "")) if "%" in quota else 0
        alert = quota_val < 10 # Alert if less than 10%
        
        return {
            "remaining": quota,
            "reset": "check CLI",
            "alert": alert,
            "error": None
        }
    except Exception as e:
        return {"remaining": "?", "reset": "?", "alert": True, "error": str(e)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_cli_fetch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ai_status.5m.py tests/test_cli_fetch.py
git commit -m "feat: add codex and antigravity CLI fetching logic"
```

---

### Task 3: HTTP Data Fetching (Z AI)

**Files:**
- Modify: `ai_status.5m.py`
- Create: `tests/test_http_fetch.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_http_fetch.py
import unittest
from unittest.mock import patch, MagicMock
import importlib.util

spec = importlib.util.spec_from_file_location("ai_status", "ai_status.5m.py")
ai_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_status)

class TestHttpFetch(unittest.TestCase):
    @patch('urllib.request.urlopen')
    def test_get_zai(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"data": {"remaining_requests": 85, "next_reset_time": "18:00"}}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = ai_status.get_zai_data("fake_key")
        self.assertEqual(result['remaining'], "85")
        self.assertEqual(result['reset'], "18:00")
        self.assertFalse(result['alert'])

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_http_fetch.py -v`
Expected: FAIL with attribute error on `get_zai_data`

- [ ] **Step 3: Write minimal implementation**

```python
# ai_status.5m.py (add imports and get_zai_data)
import urllib.request
import urllib.error

def get_zai_data(api_key):
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return {"remaining": "?", "reset": "?", "alert": True, "error": "Invalid API Key"}
        
    try:
        req = urllib.request.Request(
            "https://api.z.ai/api/monitor/usage/quota/limit",
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read())
            
        remaining = data.get("data", {}).get("remaining_requests", 0)
        reset_time = data.get("data", {}).get("next_reset_time", "?")
        
        alert = int(remaining) < 10
        
        return {
            "remaining": str(remaining),
            "reset": reset_time,
            "alert": alert,
            "error": None
        }
    except Exception as e:
        return {"remaining": "?", "reset": "?", "alert": True, "error": str(e)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_http_fetch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ai_status.5m.py tests/test_http_fetch.py
git commit -m "feat: add HTTP fetching for Z AI"
```

---

### Task 4: UI Rendering

**Files:**
- Modify: `ai_status.5m.py`
- Create: `tests/test_ui_render.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ui_render.py
import unittest
import importlib.util
from io import StringIO
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("ai_status", "ai_status.5m.py")
ai_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_status)

class TestUIRender(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_render_output(self, mock_stdout):
        codex = {"remaining": "45k", "reset": "12m", "alert": False, "error": None}
        ag = {"remaining": "82%", "reset": "1h", "alert": True, "error": None}
        zai = {"remaining": "85", "reset": "18:00", "alert": False, "error": None}
        
        ai_status.render_ui(codex, ag, zai)
        
        output = mock_stdout.getvalue()
        self.assertIn("🤖 CX: 45k", output)
        self.assertIn("🚀 AG: 82% | color=red", output) # alert should add red
        self.assertIn("⚡️ Z: 85", output)
        self.assertIn("refresh=true", output)

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_ui_render.py -v`
Expected: FAIL 

- [ ] **Step 3: Write minimal implementation**

```python
# ai_status.5m.py (replace __main__ block and add render_ui)
def format_item(emoji, prefix, data):
    base = f"{emoji} {prefix}: {data['remaining']}"
    if data['alert']:
        base += " | color=red"
    return base

def render_ui(codex, ag, zai):
    cx_str = format_item("🤖", "CX", codex)
    ag_str = format_item("🚀", "AG", ag)
    zai_str = format_item("⚡️", "Z", zai)
    
    print(f"{cx_str} | {ag_str} | {zai_str}")
    print("---")
    
    print(f"🤖 Codex: {codex['remaining']} (Reset in {codex['reset']})")
    if codex['error']: print(f"Error: {codex['error']}")
    print("---")
    
    print(f"🚀 Antigravity: {ag['remaining']} (Reset in {ag['reset']})")
    if ag['error']: print(f"Error: {ag['error']}")
    print("---")
    
    print(f"⚡️ Z AI: {zai['remaining']} (Next Reset: {zai['reset']})")
    if zai['error']: print(f"Error: {zai['error']}")
    print("---")
    
    print("🔄 Force Refresh Data | refresh=true")

if __name__ == "__main__":
    import sys
    config = load_config()
    
    codex_data = get_codex_data()
    ag_data = get_antigravity_data()
    zai_data = get_zai_data(config.get("Z_AI_API_KEY", ""))
    
    render_ui(codex_data, ag_data, zai_data)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_ui_render.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ai_status.5m.py tests/test_ui_render.py
git commit -m "feat: implement UI rendering logic for SwiftBar"
```
