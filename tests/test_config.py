import unittest
import os
import json
import importlib.util

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a clean environment
        if os.path.exists('.config.json'):
            os.remove('.config.json')
            
    def test_config_generation(self):
        # Dynamically import the script to test its functions
        spec = importlib.util.spec_from_file_location("ai_status", "ai_status.5m.py")
        ai_status = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai_status)
        
        config = ai_status.load_config()
        
        self.assertTrue(os.path.exists('.config.json'))
        self.assertIn('Z_AI_API_KEY', config)
        self.assertEqual(config['Z_AI_API_KEY'], 'YOUR_API_KEY_HERE')

if __name__ == '__main__':
    unittest.main()
