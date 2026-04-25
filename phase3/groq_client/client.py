import os
import json
from groq import Groq

class GroqClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, context: str) -> dict:
        if not self.client: return {"error": "Groq key missing"}
        
        system_prompt = """
        Analyze the following app reviews. Provide:
        1. Top 5 themes.
        2. 3 Golden quotes.
        3. 3 Action items.
        4. Summary (150-250 words).
        Output valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}
