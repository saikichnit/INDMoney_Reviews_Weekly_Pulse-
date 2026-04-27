import os
import json
from groq import Groq
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

class NoteService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_note(self, themes: list, reviews: list) -> dict:
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
        
        # Try Groq First
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Groq note generation failed, trying Gemini: {e}")
                if "rate_limit" not in str(e).lower() and "429" not in str(e):
                    if "client" not in str(e).lower(): raise e

        # Fallback to Gemini
        if self.gemini_key:
            try:
                response = self.gemini_model.generate_content(prompt)
                # Parse JSON from Gemini text (it might include markdown blocks)
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                return json.loads(text)
            except Exception as e:
                print(f"Gemini note generation failed: {e}")

        return {
            "summary": "AI Synthesis Failed. Both Groq and Gemini limits exceeded.",
            "quotes": [],
            "action_items": []
        }
