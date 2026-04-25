class Aggregator:
    def __init__(self):
        pass

    def aggregate(self, groq_out: dict, gemini_out: dict) -> dict:
        # 1. Fallback Strategy (Option C)
        if "error" in groq_out and "error" not in gemini_out:
            return gemini_out
        if "error" in gemini_out and "error" not in groq_out:
            return groq_out
        if "error" in groq_out and "error" in gemini_out:
            return {"error": "Both LLMs failed", "details": {"groq": groq_out, "gemini": gemini_out}}

        # 2. Merge Strategy (Option B)
        # We take themes from both and deduplicate (pick top 5)
        combined_themes = list(set(groq_out.get('themes', []) + gemini_out.get('themes', [])))[:5]
        
        # We prefer Groq for summary (if compliant) or Gemini if Groq is too short
        groq_summary = groq_out.get('summary', '')
        gemini_summary = gemini_out.get('summary', '')
        
        final_summary = groq_summary if len(groq_summary.split()) >= 150 else gemini_summary

        # Combine action items
        combined_actions = list(set(groq_out.get('action_items', []) + gemini_out.get('action_items', [])))[:3]

        return {
            "summary": final_summary,
            "themes": combined_themes,
            "quotes": groq_out.get('quotes', [])[:3], # Prefer Groq's quote extraction
            "action_items": combined_actions,
            "metadata": {
                "strategy": "Merge",
                "groq_status": "OK",
                "gemini_status": "OK"
            }
        }
