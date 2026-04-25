import os
from datetime import datetime

class MCPService:
    def __init__(self, export_path: str = "data/mcp_export.md"):
        self.export_path = export_path
        os.makedirs(os.path.dirname(self.export_path), exist_ok=True)

    def append_to_docs(self, report_data: dict):
        """
        Mocks the MCP behavior by appending the report to a markdown file
        representing a Google Doc.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        pulse = report_data.get('weekly_pulse', {})
        fees = report_data.get('fee_scenarios', [])
        
        content = f"""
# INDMoney Weekly Pulse - {timestamp}

## Executive Summary
{pulse.get('summary', 'No summary available.')}

## Top Themes
{chr(10).join([f"- {t}" for t in pulse.get('themes', [])])}

## Actionable Recommendations
{chr(10).join([f"- {a}" for a in pulse.get('action_items', [])])}

## Financial Education (Fees)
"""
        for fee in fees:
            content += f"\n### {fee.get('scenario_name')}\n"
            content += "\n".join([f"- {b}" for b in fee.get('explanation_bullets', [])])
            content += "\n\n**Sources:** " + ", ".join(fee.get('source_links', [])) + "\n"

        content += "\n---\n"
        
        try:
            with open(self.export_path, "a") as f:
                f.write(content)
            print(f"SUCCESS: MCP Exported to {self.export_path}")
            return True
        except Exception as e:
            print(f"ERROR: MCP Export failed: {e}")
            return False
