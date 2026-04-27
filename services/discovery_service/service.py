import os
from groq import Groq

class DiscoveryService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def discover_signals(self, reviews: list) -> list:
        if not self.client: 
            return ["AI Client Initialization Failed. GROQ_API_KEY is missing from GitHub Secrets."]
        
        context = "\n".join([f"- {r['review_text']}" for r in reviews[:100]])
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
            print(f"Discovery error: {e}")
            return []
