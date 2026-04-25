import os
from groq import Groq
import json

class ClassificationService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def classify_themes(self, signals: list) -> dict:
        if not self.client: return {"themes": []}
        
        prompt = f"""
        Group these raw signals into 3-5 high-level actionable themes for a product team.
        For each theme, estimate its distribution percentage (%) based on the frequency of similar signals.
        SIGNALS:
        {signals}
        
        Return JSON format: {{"themes": [{{"name": "Theme Name", "percentage": 45}}, ...]}}
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Classification error: {e}")
            return {"themes": []}
