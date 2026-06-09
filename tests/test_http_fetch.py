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
        # Mock payload containing both TIME_LIMIT and TOKENS_LIMIT
        mock_response.read.return_value = b'{"success": true, "data": {"limits": [{"type": "TIME_LIMIT", "remaining": 85, "percentage": 15, "nextResetTime": 1781446875995}, {"type": "TOKENS_LIMIT", "percentage": 5}]}}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = ai_status.get_zai_data("fake_key")
        self.assertEqual(result['remaining_mcp'], 85)
        self.assertEqual(result['percent_mcp'], 85)
        self.assertEqual(result['percent_tokens'], 95)
        self.assertTrue(isinstance(result['reset_mcp'], str))
        self.assertNotEqual(result['reset_mcp'], "?")
        self.assertFalse(result['alert'])

if __name__ == '__main__':
    unittest.main()
