import asyncio
import os
from groq_client.client import GroqClient
from gemini_client.client import GeminiClient
# Importing Phase 2 services for logic reuse
from phase2.services.discovery_service.service import DiscoveryService
from phase2.services.classification_service.service import ClassificationService
from phase2.services.note_service.service import NoteService
from phase2.services.email_service.service import EmailDeliveryService

class ParallelOrchestratorV3:
    def __init__(self):
        self.groq = GroqClient()
        self.gemini = GeminiClient()
        
    async def run_pipeline(self, reviews: list) -> dict:
        # Prepare context
        context = "\n".join([f"- {r['review_text']}" for r in reviews[:200]])
        
        # Parallel Execution for all 4 stages (Simulated as a single combined expert prompt for performance in Phase 3)
        # In a real large scale app, each stage could be its own parallel call.
        
        groq_task = asyncio.to_thread(self.groq.analyze, context)
        gemini_task = asyncio.to_thread(self.gemini.analyze, context)
        
        results = await asyncio.gather(groq_task, gemini_task, return_exceptions=True)
        
        # Simple Aggregation (Merge Strategy)
        groq_res = results[0] if not isinstance(results[0], Exception) else {}
        gemini_res = results[1] if not isinstance(results[1], Exception) else {}
        
        # Merge themes and summary
        merged_themes = list(set(groq_res.get('themes', []) + gemini_res.get('themes', [])))[:5]
        
        # Weekly Note Synthesis
        summary = groq_res.get('summary', '') if len(groq_res.get('summary', '').split()) > 100 else gemini_res.get('summary', '')
        
        final_report = {
            "summary": summary,
            "themes": merged_themes,
            "quotes": groq_res.get('quotes', [])[:3],
            "action_items": gemini_res.get('action_items', [])[:3],
            "email_draft": {
                "subject": "Advanced Weekly Pulse (Dual-LLM)",
                "body": f"Aggregated Summary: {summary[:100]}..."
            }
        }
        
        return final_report
