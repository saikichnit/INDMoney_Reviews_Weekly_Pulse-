import os
import json
import google.generativeai as genai
from typing import Dict

class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash" 

    def analyze(self, context: str) -> Dict:
        if not self.api_key: return {"error": "Gemini key missing"}
        
        # Heuristic for Phase 3 prompt enrichment
        prompt = f"""
        Analyze these INDMoney app reviews as a Product Manager.
        Return a JSON object with:
        - summary: 150-250 words summary.
        - themes: List of top 5 themes.
        - quotes: List of 3 impactful quotes.
        - action_items: List of 3 product recommendations.

        REVIEWS:
        {context}
        """

        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            # Simple fallback to 1.5 if 2.0 fails
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                return json.loads(response.text)
            except:
                return {"error": str(e)}
