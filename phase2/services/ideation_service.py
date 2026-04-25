import os
import json
from groq import Groq
from storage.db import DatabaseManager

class IdeationService:
    def __init__(self):
        self.db = DatabaseManager()
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def generate_product_ideas(self):
        """
        Analyzes negative reviews to suggest product improvements or identify bugs.
        """
        # Fetch recent negative reviews
        with self.db._get_connection() as conn:
            conn.row_factory = self.db.sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, review_text FROM filtered_reviews WHERE sentiment = 'Negative' ORDER BY review_date DESC LIMIT 20")
            neg_reviews = [dict(row) for row in cursor.fetchall()]

        if not neg_reviews:
            return []

        reviews_text = "\n".join([f"- {r['review_text']}" for r in neg_reviews])
        
        prompt = f"""
        Analyze these negative user reviews and generate 3 high-impact product improvement ideas or bug reports.
        Format your response as a JSON list of objects with 'title', 'description', and 'type' (bug/feature).
        
        Reviews:
        {reviews_text}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                response_format={"type": "json_object"}
            )
            response = json.loads(chat_completion.choices[0].message.content)
            ideas = response.get('ideas', [])
            
            # Save to DB
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                for idea in ideas:
                    cursor.execute('''
                        INSERT INTO ideas (title, description, type, created_at)
                        VALUES (?, ?, ?, datetime('now'))
                    ''', (idea.get('title'), idea.get('description'), idea.get('type')))
                conn.commit()
            
            return ideas
        except Exception as e:
            print(f"Ideation Error: {e}")
            return []

    def get_all_ideas(self):
        with self.db._get_connection() as conn:
            conn.row_factory = self.db.sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ideas ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
