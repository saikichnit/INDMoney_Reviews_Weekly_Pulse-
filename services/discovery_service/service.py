import os
import time
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

class DiscoveryService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def discover_signals(self, reviews: list) -> list:
        if not self.client: 
            return ["AI Client Initialization Failed. GROQ_API_KEY is missing from GitHub Secrets."]
        
        context = "\n".join([f"- {r['review_text']}" for r in reviews[:300]])
        prompt = f"""
        Extract the top 10 raw signals (topics, bugs, or feature requests) from these reviews.
        REVIEWS:
        {context}
        
        Return a simple list of signals.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model
            )
            signals = response.choices[0].message.content.strip().split('\n')
            return [s.strip('- ').strip() for s in signals if s.strip()]
        except Exception as e:
            if "rate_limit_exceeded" in str(e).lower() or "429" in str(e):
                raise e # Trigger tenacity retry
            print(f"Discovery error: {e}")
            return [f"AI Synthesis Failed. Error: {str(e)}.. Please check your GROQ_API_KEY GitHub Secret or Rate Limits."]
