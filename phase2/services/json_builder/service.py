import os
import json
from datetime import datetime

class JSONBuilder:
    def __init__(self, storage_dir: str = "data/reports"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def build_combined_payload(self, note: dict, themes: list, fee_scenarios: list = None) -> dict:
        """
        Assembles the report data into the strict Combined JSON Schema.
        """
        # Handle fee scenario (picking the first one for the root schema or null)
        main_fee = {}
        if fee_scenarios and len(fee_scenarios) > 0:
            main_fee = fee_scenarios[0]
        
        payload = {
            "id": datetime.now().strftime("%Y%m%d%H%M"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weekly_pulse": {
                "summary": note.get('summary', 'Elite synthesis pending...'),
                "themes": themes, 
                "quotes": note.get('quotes', []),
                "action_items": note.get('action_items', [])
            },
            "fee_scenarios": fee_scenarios, # Full list for MCP and Delivery
            "last_checked": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Local Persistence
        filename = f"combined-{payload['date']}.json"
        filepath = os.path.join(self.storage_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(payload, f, indent=2)
            print(f"SUCCESS: JSON persisted to {filepath}")
        except Exception as e:
            print(f"WARNING: Local JSON persistence failed: {e}")

        return payload, filepath
