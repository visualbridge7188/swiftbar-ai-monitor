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
        codex = {
            "percent_5h": 45,
            "percent_7d": 42,
            "reset_5h": "12m",
            "reset_7d": "1d 22h",
            "expected_7d": 50.0,
            "alert": False,
            "error": None
        }
        ag = {
            "models": {
                "claude": {"label": "Claude Sonnet 4.6", "percent": 100, "reset": "1h 35m"},
                "gemini_pro": {"label": "Gemini 3.1 Pro", "percent": 82, "reset": "1h 5m"},
                "gemini_flash": {"label": "Gemini 3.5 Flash", "percent": 60, "reset": "1h 5m"}
            },
            "alert": True,
            "error": None
        }
        zai = {
            "percent_mcp": 85,
            "remaining_mcp": 85,
            "reset_mcp": "18:00",
            "percent_tokens": 95,
            "alert": False,
            "error": None
        }
        
        ai_status.render_ui(codex, ag, zai)
        
        output = mock_stdout.getvalue()
        # Verify the menu bar has a single space, sparkles icon, and sfcolor=red (since ag['alert'] is True)
        self.assertIn(" | sfimage=sparkles sfcolor=red", output)
        # Verify labels and image tags are shown in the dropdown lines
        self.assertIn("• 5-Hour Limit: 45% remaining", output)
        self.assertIn("• 7-Day Limit : 42% remaining", output)
        self.assertIn("• Claude (Claude Sonnet 4.6): 100% remaining", output)
        self.assertIn("• Gemini Pro (Gemini 3.1 Pro): 82% remaining", output)
        self.assertIn("• Gemini Flash (Gemini 3.5 Flash): 60% remaining", output)
        self.assertIn("• MCP Calls   : 85 remaining (85%)", output)
        self.assertIn("• Model Tokens: 95% remaining", output)
        self.assertIn("| image=", output)
        self.assertIn("disabled=true", output)
        self.assertIn("refresh=true", output)

if __name__ == '__main__':
    unittest.main()
