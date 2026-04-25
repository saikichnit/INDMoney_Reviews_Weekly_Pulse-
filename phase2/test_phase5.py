import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'phase2'))

import unittest
from services.json_builder.service import JSONBuilder
from services.mcp_service.mcp_client import MCPClient

class TestPhase5(unittest.TestCase):
    def setUp(self):
        self.builder = JSONBuilder(storage_dir="data/test_reports")
        self.client = MCPClient()

    def test_json_schema_validation(self):
        note = {
            "summary": "Sample summary",
            "quotes": ["Quote 1"],
            "action_items": ["Action 1"]
        }
        themes = ["Performance", "UX"]
        fees = [{
            "scenario_name": "Exit Load",
            "explanation_bullets": ["Bullet 1"],
            "source_links": ["Link 1"],
            "last_checked": "2026-04-24"
        }]
        
        payload = self.builder.build_combined_payload(note, themes, fees)
        
        self.assertIn("weekly_pulse", payload)
        self.assertEqual(payload["fee_scenario"], "Exit Load")
        self.assertEqual(len(payload["weekly_pulse"]["themes"]), 2)
        print("✓ JSON Schema Validation Passed")

    def test_skip_logic(self):
        # Temporarily clear env var
        old_id = os.environ.get("GOOGLE_DOC_ID")
        os.environ["GOOGLE_DOC_ID"] = ""
        
        client = MCPClient()
        success = client.append_to_google_docs({"data": "test"})
        
        self.assertFalse(success)
        print("✓ Skip Logic (No ID) Passed")
        
        if old_id: os.environ["GOOGLE_DOC_ID"] = old_id

if __name__ == "__main__":
    unittest.main()
