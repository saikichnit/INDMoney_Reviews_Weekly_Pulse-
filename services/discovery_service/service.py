import os
import time
from groq import Groq
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class DiscoveryService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=4, max=10))
    def discover_signals(self, reviews: list) -> list:
        # Limit context to stay within TPM limits (80 reviews max for safety)
        context = "\n".join([f"- {r['review_text']}" for r in reviews[:80]])
        prompt = f"""
        Extract the top 10 raw signals (topics, bugs, or feature requests) from these reviews.
        REVIEWS:
        {context}
        
        Return a simple list of signals.
        """
        
        # Try Groq First
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model
                )
                signals = response.choices[0].message.content.strip().split('\n')
                return [s.strip('- ').strip() for s in signals if s.strip()]
            except Exception as e:
                print(f"Groq failed, trying Gemini fallback: {e}")
                if "rate_limit" not in str(e).lower() and "429" not in str(e):
                    # If it's NOT a rate limit, don't fallback yet, let retry handle it
                    if "client" not in str(e).lower(): raise e

        # Fallback to Gemini
        if self.gemini_key:
            try:
                response = self.gemini_model.generate_content(prompt)
                signals = response.text.strip().split('\n')
                return [s.strip('- ').strip() for s in signals if s.strip()]
            except Exception as e:
                print(f"Gemini also failed: {e}")
        
        return ["AI Synthesis Failed. Both Groq (Rate Limited) and Gemini (Fallback) failed."]
