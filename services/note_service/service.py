import os
from groq import Groq
import json

class NoteService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def generate_note(self, themes: list, reviews: list) -> dict:
        if not self.client: return {}
        
        # Take a few representative reviews for quotes
        context = "\n".join([f"- {r['review_text']}" for r in reviews[:50]])
        
        prompt = f"""
        Generate a Weekly Review Pulse based on these themes: {themes}.
        Use these reviews for context: {context}
        
        CONSTRAINTS:
        1. Summary <= 250 words.
        2. Exactly 3 anonymized quotes.
        3. Exactly 3 action items.
        
        Return JSON: {{
            "summary": "...",
            "quotes": ["...", "...", "..."],
            "action_items": ["...", "...", "..."]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Note generation error: {e}")
            return {}
