import os
import json
from groq import Groq

class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def _chunk_reviews(self, reviews: list, chunk_size: int = 200):
        for i in range(0, len(reviews), chunk_size):
            yield reviews[i:i + chunk_size]

    def analyze_reviews(self, reviews: list) -> dict:
        if not self.client:
            return {"error": "GROQ_API_KEY missing"}

        # 1. Map Phase: Extract themes from all batches
        all_batch_themes = []
        all_batch_quotes = []
        
        for chunk in self._chunk_reviews(reviews, chunk_size=200):
            context = "\n".join([f"- [Rating: {r['rating']}] {r['review_text']}" for r in chunk])
            
            prompt = f"""
            Analyze these reviews and return a JSON with:
            - themes: list of top 3 themes in this batch
            - quotes: 2 representative quotes
            
            REVIEWS:
            {context}
            """
            
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    response_format={"type": "json_object"}
                )
                res = json.loads(response.choices[0].message.content)
                all_batch_themes.extend(res.get('themes', []))
                all_batch_quotes.extend(res.get('quotes', []))
            except Exception as e:
                print(f"Error in batch processing: {e}")

        # 2. Reduce Phase: Consolidate into final report
        system_prompt = """
        You are a Lead Product Analyst at INDMoney. 
        You will be given a list of themes and quotes collected from 1,000 user reviews.
        Your task is to synthesize them into one final master report.
        
        STRICT CONSTRAINTS:
        1. Max 5 global themes.
        2. Exactly 3 anonymized quotes (pick the most impactful).
        3. Exactly 3 actionable recommendations.
        4. Summary length: 150-250 words.
        5. Output JSON only.
        """

        reduction_prompt = f"""
        CONSOLIDATED DATA FROM ALL REVIEWS:
        THEMES: {all_batch_themes}
        QUOTES: {all_batch_quotes}
        
        Generate the final Weekly Pulse JSON:
        """

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": reduction_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": f"Synthesis failed: {str(e)}"}
