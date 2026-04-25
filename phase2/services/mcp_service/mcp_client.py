from services.mcp_service.google_docs_helper import GoogleDocsHelper
import os
import json
from dotenv import load_dotenv

class MCPClient:
    def __init__(self):
        load_dotenv()
        self.doc_id = os.environ.get("GOOGLE_DOC_ID")
        self.helper = GoogleDocsHelper()

    def append_to_google_docs(self, payload: dict) -> bool:
        """
        Appends the JSON payload to a Google Doc.
        Fully configured via .env variables.
        """
        if not self.doc_id:
            print("Phase 5 skipped: GOOGLE_DOC_ID not configured in .env")
            return False

        try:
            pulse = payload.get('weekly_pulse', {})
            date = payload.get('date', 'Unknown Date')
            
            # Elite Strategic Formatting
            content = f"\n{'='*60}\n"
            content += f"INDPLUS STRATEGIC INTELLIGENCE PULSE | {date}\n"
            content += f"{'='*60}\n\n"
            
            content += "⚡ EXECUTIVE SPOTLIGHT\n"
            content += f"{pulse.get('summary', 'No summary available.')}\n\n"
            
            content += "📊 STRATEGIC THEME ANALYSIS\n"
            for theme in pulse.get('themes', []):
                name = theme.get('name') if isinstance(theme, dict) else theme
                percent = theme.get('percentage') if isinstance(theme, dict) else "?"
                content += f"  • {name} | {percent}% Impact\n"
            content += "\n"
            
            content += "🗣️ VOICE OF CUSTOMER: CRITICAL SIGNALS\n"
            for quote in pulse.get('quotes', []):
                content += f"  > \"{quote}\"\n"
            content += "\n"
            
            content += "🚀 STRATEGIC ACTION ROADMAP\n"
            for action in pulse.get('action_items', []):
                content += f"  - {action}\n"
            content += "\n"
            
            # 🎓 Financial Education Sync
            fee_data = payload.get('fee_scenarios') or [payload.get('main_fee')] if payload.get('main_fee') else []
            if fee_data:
                content += "🎓 STRATEGIC FINANCIAL EDUCATION\n"
                for fee in fee_data:
                    if not fee: continue
                    content += f"  • {fee.get('scenario_name')}\n"
                    for bullet in fee.get('explanation_bullets', []):
                        clean_bullet = str(bullet).replace('\u2022', '-')
                        content += f"    - {clean_bullet}\n"
                    if fee.get('source_links'):
                        content += f"    Source: {fee.get('source_links')[0]}\n"
                content += "\n"
            
            content += f"\nReport ID: {payload.get('id', 'N/A')} | Source: Automated Pipeline\n"
            content += f"{'='*60}\n"
            
            return self.helper.sync_report(content)
        except Exception as e:
            print(f"ERROR: Phase 5 (MCP) failed: {e}")
            return False
