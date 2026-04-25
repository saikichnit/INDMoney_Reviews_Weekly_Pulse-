import os
import json
from groq import Groq

class GroqOrchestrator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def generate_report(self, reviews: list) -> dict:
        if not self.client:
            return {"error": "GROQ_API_KEY not configured."}

        review_context = "\n".join([
            f"- [Rating: {r['rating']}] {r['review_text']}"
            for r in reviews[:200] # Representative sample for Phase 1 tokens
        ])

        system_prompt = """
        You are a Product Analyst at INDMoney. Analyze app reviews and generate a Weekly Pulse.
        
        STRICT CONSTRAINTS:
        1. Identify 3-5 distinct, actionable themes.
        2. Provide 3 representative user quotes (anonymized).
        3. Provide 3 actionable recommendations.
        4. Summary MUST be ≤ 250 words.
        5. NO PII (emails, phones, etc.) in output.
        6. Output MUST be valid JSON with keys: 'summary', 'themes', 'quotes', 'action_items', 'email_draft'.
        """

        user_prompt = f"REVIEWS:\n{review_context}\n\nGenerate report JSON:"

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}
