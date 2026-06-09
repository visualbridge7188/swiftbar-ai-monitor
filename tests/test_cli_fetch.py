import unittest
from unittest.mock import patch, MagicMock
import importlib.util

import sys
spec = importlib.util.spec_from_file_location("ai_status", "ai_status.5m.py")
ai_status = importlib.util.module_from_spec(spec)
sys.modules['ai_status'] = ai_status
spec.loader.exec_module(ai_status)

class TestCliFetch(unittest.TestCase):
    @patch('os.path.exists')
    @patch('glob.glob')
    @patch('os.path.getmtime', return_value=12345)
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"payload": {"rate_limits": {"primary": {"used_percent": 57.0, "resets_at": 1718000000}, "secondary": {"used_percent": 58.0, "resets_at": 1718100000}}}}')
    @patch('time.time', return_value=1718000000 - 720) # 1717999280
    def test_get_codex(self, mock_time, mock_file, mock_mtime, mock_glob, mock_exists):
        mock_exists.return_value = True
        mock_glob.return_value = ["/fake/path/session.jsonl"]
        
        result = ai_status.get_codex_data()
        self.assertEqual(result['percent_5h'], 43)
        self.assertEqual(result['percent_7d'], 42)
        self.assertEqual(result['reset_5h'], "12m 0s")
        self.assertEqual(result['reset_7d'], "1d 3h")
        self.assertFalse(result['alert'])

    @patch('ai_status.detect_antigravity_process', return_value=(None, None))
    @patch('subprocess.run')
    def test_get_antigravity_cli_fallback(self, mock_run, mock_detect):
        mock_result = MagicMock()
        mock_result.stdout = '{"model_quota": {"gemini-pro": "82%"}, "next_reset_epoch": 0}'
        mock_run.return_value = mock_result
        
        result = ai_status.get_antigravity_data()
        self.assertEqual(result['models']['gemini_pro']['percent'], 82)
        self.assertEqual(result['models']['claude']['percent'], 100)
        self.assertEqual(result['models']['gemini_flash']['percent'], 60)
        self.assertFalse(result['alert'])

    @patch('ai_status.detect_antigravity_process')
    @patch('ai_status.get_listening_ports')
    @patch('ai_status.query_antigravity_status')
    def test_get_antigravity_local_success(self, mock_query, mock_ports, mock_detect):
        mock_detect.return_value = (12345, "csrf-123")
        mock_ports.return_value = [60555]
        mock_query.return_value = {
            "userStatus": {
                "email": "test@example.com",
                "cascadeModelConfigData": {
                    "clientModelConfigs": [
                        {
                            "label": "Claude Sonnet 4.6 (Thinking)",
                            "modelOrAlias": {"model": "claude-3-5-sonnet"},
                            "quotaInfo": {"remainingFraction": 0.9, "resetTime": "2026-06-09T15:35:49Z"}
                        },
                        {
                            "label": "Gemini 3.1 Pro (High)",
                            "modelOrAlias": {"model": "gemini-1.5-pro"},
                            "quotaInfo": {"remainingFraction": 0.6, "resetTime": "2026-06-09T14:38:42Z"}
                        },
                        {
                            "label": "Gemini 3.5 Flash (High)",
                            "modelOrAlias": {"model": "gemini-1.5-flash"},
                            "quotaInfo": {"remainingFraction": 0.4, "resetTime": "2026-06-09T14:38:42Z"}
                        }
                    ]
                }
            }
        }
        
        result = ai_status.get_antigravity_data()
        self.assertFalse(result['mocked'])
        self.assertIsNone(result['error'])
        
        models = result['models']
        self.assertEqual(models['claude']['percent'], 90)
        self.assertEqual(models['gemini_pro']['percent'], 60)
        self.assertEqual(models['gemini_flash']['percent'], 40)
        self.assertFalse(result['alert'])

if __name__ == '__main__':
    unittest.main()
