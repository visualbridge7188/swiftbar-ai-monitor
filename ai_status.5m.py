#!/opt/homebrew/bin/python3
# <bitbar.title>AI Tools Total Monitor</bitbar.title>
# <bitbar.version>v1.6</bitbar.version>
# <bitbar.author>User</bitbar.author>
# <bitbar.desc>Monitors Codex, Antigravity, and Z AI tokens natively</bitbar.desc>

import os
import json
import subprocess
import urllib.request
import urllib.error
import glob
import time
import base64
import re
import datetime
from io import BytesIO

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Prepend standard binary search paths for SwiftBar environment
extra_paths = ["/usr/local/bin", "/opt/homebrew/bin", os.path.expanduser("~/.codex/bin")]
for path in extra_paths:
    if path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{path}:{os.environ.get('PATH', '')}"

def generate_progress_bar_image(percent, expected_percent=None):
    if not HAS_PIL:
        return ""
    # Draw a progress bar: Width=160, Height=12
    width, height = 160, 12
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Track (semi-transparent gray)
    draw.rounded_rectangle([0, 2, width, height - 2], radius=4, fill=(120, 120, 120, 50))
    
    # 2. Fill
    # Standard blue: (59, 130, 246, 255)
    # Alert (< 10% remaining): (239, 68, 68, 255) (red)
    fill_color = (239, 68, 68, 255) if percent < 10 else (59, 130, 246, 255)
    fill_width = int(width * (percent / 100.0))
    if fill_width > 0:
        draw.rounded_rectangle([0, 2, fill_width, height - 2], radius=4, fill=fill_color)
        
    # 3. Pacing Line
    if expected_percent is not None:
        expected_x = int(width * (expected_percent / 100.0))
        if 0 < expected_x < width:
            # Over-budget warning: actual remaining is LESS than expected remaining (i.e. used more)
            is_deficit = percent < expected_percent - 2.0
            marker_color = (239, 68, 68, 255) if is_deficit else (34, 197, 94, 255) # Red vs Green
            
            # Draw a black line of width 4 as a visual separator/punch-out
            draw.line([expected_x, 0, expected_x, height], fill=(30, 30, 30, 255), width=4)
            # Draw the colored pacing line of width 2 inside it
            draw.line([expected_x, 0, expected_x, height], fill=marker_color, width=2)

    # Convert to base64
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Use a hidden .config.json file to prevent SwiftBar from loading it as a plugin
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '.config.json')

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

def format_time(seconds):
    if seconds >= 86400:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"
    elif seconds >= 3600:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
    elif seconds >= 60:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    else:
        return f"{seconds}s"

def get_codex_data():
    MAX_FILE_AGE_SECONDS = 86400  # Only consider files modified within 24 hours

    try:
        sessions_dir = os.path.expanduser("~/.codex/sessions")
        if not os.path.exists(sessions_dir):
            raise Exception("Sessions directory not found")
            
        search_path = os.path.join(sessions_dir, "**", "*.jsonl")
        files = glob.glob(search_path, recursive=True)
        if not files:
            raise Exception("No active session files found")
            
        # Sort files by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        now = time.time()

        # Scan multiple files (not just the newest) to find valid rate_limits.
        # The newest file may have primary=null, secondary=null (e.g. limit_id="premium").
        rate_limits = None
        source_file = None
        for fpath in files:
            # Skip files older than 24 hours
            if now - os.path.getmtime(fpath) > MAX_FILE_AGE_SECONDS:
                break

            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for line in reversed(lines):
                    try:
                        obj = json.loads(line)
                        if "payload" in obj and "rate_limits" in obj["payload"]:
                            rl = obj["payload"]["rate_limits"]
                            # Accept entries with valid primary AND secondary
                            if rl and rl.get("primary") and rl.get("secondary"):
                                rate_limits = rl
                                source_file = fpath
                                break
                    except Exception:
                        continue
                if rate_limits:
                    break
            except Exception:
                continue
                    
        if not rate_limits:
            raise Exception("No rate limit data found in recent sessions")
            
        primary = rate_limits["primary"]
        secondary = rate_limits["secondary"]
        
        reset_p_ts = primary.get("resets_at", 0)
        reset_s_ts = secondary.get("resets_at", 0)
        
        # Check if each limit's data has expired (reset time passed)
        p_expired = reset_p_ts > 0 and reset_p_ts < now
        s_expired = reset_s_ts > 0 and reset_s_ts < now
        
        # If BOTH limits expired, data is completely stale
        if p_expired and s_expired:
            data_age_h = (now - os.path.getmtime(source_file)) / 3600
            raise Exception(f"Data expired {data_age_h:.0f}h ago")
        
        # Calculate remaining for non-expired limits
        if p_expired:
            remaining_p = -1  # Unknown after reset
            reset_p_seconds = 0
        else:
            remaining_p = max(0.0, 100.0 - primary.get("used_percent", 0.0))
            reset_p_seconds = max(0, int(reset_p_ts - now))
            
        if s_expired:
            remaining_s = -1  # Unknown after reset
            reset_s_seconds = 0
        else:
            remaining_s = max(0.0, 100.0 - secondary.get("used_percent", 0.0))
            reset_s_seconds = max(0, int(reset_s_ts - now))
        
        # Calculate expected remaining for 7-day pacing (only if secondary is valid)
        expected_7d = None
        if not s_expired:
            duration_s = 604800
            time_until_reset_s = reset_s_ts - now
            if 0 < time_until_reset_s <= duration_s:
                elapsed = duration_s - time_until_reset_s
                expected_used = (elapsed / duration_s) * 100.0
                expected_7d = max(0.0, min(100.0, 100.0 - expected_used))
            
        alert = (remaining_p >= 0 and remaining_p < 10) or (remaining_s >= 0 and remaining_s < 10)

        # Determine if data is stale (source file is not the newest)
        newest_file = files[0]
        is_stale = (source_file != newest_file)
        
        # Build informative error message
        error_parts = []
        if is_stale:
            data_age_h = (now - os.path.getmtime(source_file)) / 3600
            error_parts.append(f"Updated {data_age_h:.0f}h ago")
        if p_expired:
            error_parts.append("5h: need new session")
        error_msg = f"({', '.join(error_parts)})" if error_parts else None
        
        return {
            "percent_5h": int(remaining_p) if remaining_p >= 0 else -1,
            "percent_7d": int(remaining_s) if remaining_s >= 0 else -1,
            "reset_5h": format_time(reset_p_seconds) if not p_expired else "Reset",
            "reset_7d": format_time(reset_s_seconds) if not s_expired else "Reset",
            "expected_7d": expected_7d,
            "alert": alert,
            "error": error_msg,
            "mocked": False
        }
    except Exception:
        # Keep error clean and short
        return {
            "percent_5h": -1,
            "percent_7d": -1,
            "reset_5h": "N/A",
            "reset_7d": "N/A",
            "expected_7d": None,
            "alert": False,
            "error": "(No Data)",
            "mocked": True
        }

def _parse_iso8601(val):
    if not val:
        return 0
    try:
        val = val.replace("Z", "")
        parts = val.split("T")
        date_parts = list(map(int, parts[0].split("-")))
        time_parts = list(map(float, parts[1].split(":")))
        dt = datetime.datetime(
            date_parts[0], date_parts[1], date_parts[2],
            int(time_parts[0]), int(time_parts[1]), int(time_parts[2])
        )
        return dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    except Exception:
        try:
            return float(val)
        except Exception:
            return 0

def detect_antigravity_process():
    try:
        result = subprocess.run(
            ["ps", "-ax", "-o", "pid,command"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            pid_str, cmd = parts[0], parts[1]
            cmd_lower = cmd.lower()
            is_ls = "language_server" in cmd_lower and ("antigravity" in cmd_lower or "app_data_dir" in cmd_lower)
            is_cli = "antigravity-cli" in cmd_lower or "antigravity_cli" in cmd_lower or "agy" in cmd_lower
            if is_ls or is_cli:
                csrf_token = ""
                csrf_match = re.search(r'--csrf_token[=\s]+([^\s]+)', cmd)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                return int(pid_str), csrf_token
    except Exception:
        pass
    return None, None

def get_listening_ports(pid):
    try:
        result = subprocess.run(
            ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN", "-a", "-p", str(pid)],
            capture_output=True,
            text=True,
            check=True
        )
        ports = []
        for match in re.finditer(r':(\d+)\s+\(LISTEN\)', result.stdout):
            ports.append(int(match.group(1)))
        return sorted(list(set(ports)))
    except Exception:
        return []

def query_antigravity_status(port, csrf_token):
    url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUserStatus"
    body = {
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "ideVersion": "unknown",
            "locale": "en"
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Connect-Protocol-Version": "1",
    }
    if csrf_token:
        headers["X-Codeium-Csrf-Token"] = csrf_token
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        return query_antigravity_configs(port, csrf_token)
    except Exception:
        return None

def query_antigravity_configs(port, csrf_token):
    url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetCommandModelConfigs"
    body = {
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "ideVersion": "unknown",
            "locale": "en"
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Connect-Protocol-Version": "1",
    }
    if csrf_token:
        headers["X-Codeium-Csrf-Token"] = csrf_token
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            return json.loads(response.read())
    except Exception:
        return None

def parse_antigravity_models(res):
    if not res:
        return None
    configs = []
    if "userStatus" in res and "cascadeModelConfigData" in res["userStatus"]:
        configs = res["userStatus"]["cascadeModelConfigData"].get("clientModelConfigs", [])
    elif "clientModelConfigs" in res:
        configs = res.get("clientModelConfigs", [])
        
    family_configs = {"claude": [], "gemini_pro": [], "gemini_flash": []}
    for cfg in configs:
        label = cfg.get("label", "").lower()
        model_id = cfg.get("modelOrAlias", {}).get("model", "").lower()
        if any(k in label or k in model_id for k in ["lite", "autocomplete", "image"]):
            continue
        if model_id.startswith("tab_"):
            continue
            
        if "claude" in label or "claude" in model_id:
            family = "claude"
        elif "gemini" in label or "gemini" in model_id:
            if "pro" in label or "pro" in model_id:
                family = "gemini_pro"
            elif "flash" in label or "flash" in model_id:
                family = "gemini_flash"
            else:
                continue
        else:
            continue
        family_configs[family].append(cfg)
        
    models = {"claude": None, "gemini_pro": None, "gemini_flash": None}
    for family, cfgs in family_configs.items():
        if not cfgs:
            continue
        def sort_key(c):
            quota = c.get("quotaInfo", {})
            rem = quota.get("remainingFraction")
            rem_val = rem if rem is not None else 1.0
            reset_str = quota.get("resetTime")
            reset_val = _parse_iso8601(reset_str) if reset_str else float('inf')
            label = c.get("label", "")
            has_rem = 0 if rem is not None else 1
            return (has_rem, rem_val, reset_val, label.lower())
            
        cfgs.sort(key=sort_key)
        best = cfgs[0]
        quota = best.get("quotaInfo", {})
        rem = quota.get("remainingFraction")
        if rem is not None:
            percent = int(max(0.0, min(100.0, rem * 100.0)))
            has_quota = True
        else:
            percent = None
            has_quota = False
        reset_str = quota.get("resetTime")
        reset_seconds = max(0, int(_parse_iso8601(reset_str) - time.time())) if reset_str else 0
        
        models[family] = {
            "label": best.get("label"),
            "percent": percent,
            "has_quota": has_quota,
            "reset": format_time(reset_seconds) if reset_seconds > 0 else "N/A"
        }
    return models

def get_antigravity_data():
    try:
        pid, token = detect_antigravity_process()
        if pid:
            ports = get_listening_ports(pid)
            for port in ports:
                res = query_antigravity_status(port, token)
                models = parse_antigravity_models(res)
                # Extract credits from API response
                credits = None
                if res and "userStatus" in res:
                    plan = res["userStatus"].get("planStatus", {})
                    pi = plan.get("planInfo", {})
                    prompt_avail = plan.get("availablePromptCredits")
                    prompt_total = pi.get("monthlyPromptCredits")
                    flow_avail = plan.get("availableFlowCredits")
                    flow_total = pi.get("monthlyFlowCredits")
                    if prompt_avail is not None or flow_avail is not None:
                        credits = {
                            "prompt_available": prompt_avail or 0,
                            "prompt_total": prompt_total or 0,
                            "flow_available": flow_avail or 0,
                            "flow_total": flow_total or 0,
                        }
                if models and any(models.values()):
                    model_alert = any(m["percent"] < 10 for m in models.values() if m and m.get("percent") is not None)
                    credit_alert = False
                    if credits:
                        if credits["prompt_total"] > 0:
                            credit_alert = (credits["prompt_available"] / credits["prompt_total"] * 100) < 10
                        if credits["flow_total"] > 0:
                            credit_alert = credit_alert or (credits["flow_available"] / credits["flow_total"] * 100) < 10
                    return {
                        "models": models,
                        "credits": credits,
                        "alert": model_alert or credit_alert,
                        "error": None,
                        "mocked": False
                    }
    except Exception:
        pass
        
    try:
        result = subprocess.run(["antigravity-usage", "--status", "json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        quota = data.get("model_quota", {}).get("gemini-pro", "0%")
        quota_val = int(quota.replace("%", "")) if "%" in quota else 0
        alert = quota_val < 10
        models = {
            "claude": {"label": "Claude Sonnet 4.6 (Simulated)", "percent": 100, "reset": "1h 35m"},
            "gemini_pro": {"label": "Gemini 3.1 Pro", "percent": quota_val, "reset": "check CLI"},
            "gemini_flash": {"label": "Gemini 3.5 Flash (Simulated)", "percent": 60, "reset": "1h 05m"}
        }
        return {
            "models": models,
            "alert": alert,
            "error": None,
            "mocked": False
        }
    except Exception:
        models = {
            "claude": {"label": "Claude Sonnet 4.6 (Simulated)", "percent": 100, "reset": "1h 35m"},
            "gemini_pro": {"label": "Gemini 3.1 Pro (Simulated)", "percent": 82, "reset": "1h 05m"},
            "gemini_flash": {"label": "Gemini 3.5 Flash (Simulated)", "percent": 60, "reset": "1h 05m"}
        }
        return {
            "models": models,
            "alert": False,
            "error": "(Simulated Quota)",
            "mocked": True
        }

def get_zai_data(api_key):
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return {
            "percent_mcp": 85,
            "remaining_mcp": 85,
            "reset_mcp": "18:00",
            "percent_tokens": 90,
            "alert": False,
            "error": "(Simulated Quota - API Key Missing)",
            "mocked": True
        }
        
    try:
        req = urllib.request.Request(
            "https://api.z.ai/api/monitor/usage/quota/limit",
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read())
            
        limits = data.get("data", {}).get("limits", [])
        if not limits:
            raise Exception("No limits data in response")
            
        time_limit = None
        tokens_limit = None
        for limit in limits:
            if limit.get("type") == "TIME_LIMIT":
                time_limit = limit
            elif limit.get("type") == "TOKENS_LIMIT":
                tokens_limit = limit

        if not time_limit:
            raise Exception("No TIME_LIMIT data found in response")

        # Time Limit (MCP Calls)
        remaining_mcp = time_limit.get("remaining", 100)
        percent_mcp_used = time_limit.get("percentage", 0)
        remaining_mcp_percent = max(0, 100 - int(percent_mcp_used))
        
        reset_ms = time_limit.get("nextResetTime")
        reset_mcp_str = "?"
        if reset_ms:
            import datetime
            reset_mcp_str = datetime.datetime.fromtimestamp(reset_ms / 1000).strftime('%H:%M')

        # Tokens Limit
        remaining_tokens_percent = 100
        if tokens_limit:
            percent_tokens_used = tokens_limit.get("percentage", 0)
            remaining_tokens_percent = max(0, 100 - int(percent_tokens_used))
            
        alert = (remaining_mcp_percent < 10) or (remaining_tokens_percent < 10)
        
        return {
            "percent_mcp": remaining_mcp_percent,
            "remaining_mcp": remaining_mcp,
            "reset_mcp": reset_mcp_str,
            "percent_tokens": remaining_tokens_percent,
            "alert": alert,
            "error": None,
            "mocked": False
        }
    except Exception:
        # Keep error clean and short
        return {
            "percent_mcp": 85,
            "remaining_mcp": 85,
            "reset_mcp": "18:00",
            "percent_tokens": 90,
            "alert": False,
            "error": "(Simulated Quota)",
            "mocked": True
        }

def get_bar_text(percentage):
    filled = min(5, max(0, round(percentage / 20)))
    empty = 5 - filled
    return "█" * filled + "░" * empty

def render_ui(codex, ag, zai):
    any_alert = codex['alert'] or ag['alert'] or zai['alert']
    
    # Print the menu bar title line with a single space and sfimage sparkles icon
    # A single space before the pipe ensures SwiftBar renders the item correctly,
    # but keeps it visually clean as an icon-only display.
    title_line = " | sfimage=sparkles"
    if any_alert:
        title_line += " sfcolor=red"
        
    print(title_line)
    print("---")
    
    # Dropdown Details
    if codex['mocked'] and codex['percent_5h'] < 0 and codex['percent_7d'] < 0:
        # No session data at all - show minimal status
        print("🤖 Codex Status:")
        print(f"   • No session data available")
    else:
        print("🤖 Codex Status:")
        # 5-Hour Limit
        p5h = codex['percent_5h']
        if p5h >= 0:
            bar_cx_5h = generate_progress_bar_image(p5h) if HAS_PIL else ""
            txt_5h = f"   • 5-Hour Limit: {p5h}% remaining (Reset: {codex['reset_5h']})"
            print(txt_5h)
            if HAS_PIL:
                print(f"     | image={bar_cx_5h} disabled=true")
        else:
            print(f"   • 5-Hour Limit: ⏳ Reset — need new session | color=orange")
        
        # 7-Day Limit
        p7d = codex['percent_7d']
        if p7d >= 0:
            bar_cx_7d = generate_progress_bar_image(p7d, codex.get('expected_7d')) if HAS_PIL else ""
            txt_7d = f"   • 7-Day Limit : {p7d}% remaining (Reset: {codex['reset_7d']})"
            print(txt_7d)
            if HAS_PIL:
                print(f"     | image={bar_cx_7d} disabled=true")
        else:
            print(f"   • 7-Day Limit : ⏳ Reset — need new session | color=orange")
        
    if codex['error']: 
        print(f"     {codex['error']}")
    print("---")
    
    print("🚀 Antigravity Status:")
    ag_credits = ag.get("credits")
    if ag_credits:
        prompt_pct = round(ag_credits["prompt_available"] / ag_credits["prompt_total"] * 100) if ag_credits["prompt_total"] > 0 else 0
        flow_pct = round(ag_credits["flow_available"] / ag_credits["flow_total"] * 100) if ag_credits["flow_total"] > 0 else 0
        if HAS_PIL:
            bar_prompt = generate_progress_bar_image(prompt_pct)
            bar_flow = generate_progress_bar_image(flow_pct)
            print(f"   • Prompt Credits: {ag_credits['prompt_available']:,}/{ag_credits['prompt_total']:,} ({prompt_pct}%)")
            print(f"     | image={bar_prompt} disabled=true")
            print(f"   • Flow Credits  : {ag_credits['flow_available']:,}/{ag_credits['flow_total']:,} ({flow_pct}%)")
            print(f"     | image={bar_flow} disabled=true")
        else:
            print(f"   • Prompt Credits: {ag_credits['prompt_available']:,}/{ag_credits['prompt_total']:,} ({prompt_pct}%)")
            print(f"   • Flow Credits  : {ag_credits['flow_available']:,}/{ag_credits['flow_total']:,} ({flow_pct}%)")
        print("   ─── Model Quotas ───")
    ag_models = ag.get("models", {})
    for family, key in [("Claude", "claude"), ("Gemini Pro", "gemini_pro"), ("Gemini Flash", "gemini_flash")]:
        model = ag_models.get(key)
        if model:
            lbl = model["label"]
            pct = model["percent"]
            rst = model["reset"]
            has_quota = model.get("has_quota", True)
            if pct is not None:
                pct_display = f"{pct}%"
                bar_val = pct
            elif has_quota is False:
                pct_display = "Shared Pool ↗"
                bar_val = 0
            else:
                pct_display = "N/A"
                bar_val = 0
            if HAS_PIL:
                bar_img = generate_progress_bar_image(bar_val)
                suffix = f" (Reset: {rst})" if pct is not None else ""
                print(f"   • {family} ({lbl}): {pct_display}{suffix}")
                print(f"     | image={bar_img} disabled=true")
            else:
                bar_txt = get_bar_text(bar_val)
                suffix = f" (Reset: {rst})" if pct is not None else ""
                print(f"   • {family} ({lbl}): [{bar_txt}] {pct_display}{suffix}")
                
    if ag['error']: 
        print(f"     {ag['error']}")
    print("---")
    
    # Z.ai dual limits (MCP Calls + Tokens)
    if HAS_PIL:
        bar_zai_mcp = generate_progress_bar_image(zai['percent_mcp'])
        bar_zai_tokens = generate_progress_bar_image(zai['percent_tokens'])
        
        print("⚡️ Z AI Status:")
        print(f"   • MCP Calls   : {zai['remaining_mcp']} remaining ({zai['percent_mcp']}%) - Next Reset: {zai['reset_mcp']}")
        print(f"     | image={bar_zai_mcp} disabled=true")
        print(f"   • Model Tokens: {zai['percent_tokens']}% remaining")
        print(f"     | image={bar_zai_tokens} disabled=true")
    else:
        bar_mcp = get_bar_text(zai['percent_mcp'])
        bar_tokens = get_bar_text(zai['percent_tokens'])
        print("⚡️ Z AI Status:")
        print(f"   • MCP Calls   : [{bar_mcp}] {zai['remaining_mcp']} remaining ({zai['percent_mcp']}%) - Next Reset: {zai['reset_mcp']}")
        print(f"   • Model Tokens: [{bar_tokens}] {zai['percent_tokens']}% remaining")
        
    if zai['error']: 
        print(f"     {zai['error']}")
    print("---")
    
    if not HAS_PIL:
        print("⚠️ Pillow library not found in SwiftBar's python environment. Showing text fallback. | color=orange")
        print("---")
        
    print("🔄 Force Refresh Data | refresh=true")

if __name__ == "__main__":
    config = load_config()
    
    codex_data = get_codex_data()
    ag_data = get_antigravity_data()
    zai_data = get_zai_data(config.get("Z_AI_API_KEY", ""))
    
    render_ui(codex_data, ag_data, zai_data)
