from storage.db import DatabaseManager
from datetime import datetime, timedelta

class ReviewsService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_reviews(self, platform=None, sentiment=None, rating=None, time_range='30d', limit=5000, category=None):
        """
        Retrieves reviews with advanced platform, sentiment, and time filtering.
        """
        query = "SELECT * FROM filtered_reviews WHERE 1=1"
        params = []
        
        if platform and platform.lower() != 'all':
            query += " AND platform = ?"
            params.append(platform.lower())
            
        if sentiment and sentiment != 'All':
            query += " AND sentiment = ?"
            params.append(sentiment)

        if rating:
            query += " AND rating = ?"
            params.append(rating)

        if category:
            query += " AND category = ?"
            params.append(category)
            
        if time_range:
            days = int(time_range.replace('d', '')) if 'd' in time_range else 30
            since = (datetime.now() - timedelta(days=days)).isoformat()
            query += " AND review_date >= ?"
            params.append(since)
            
        query += " ORDER BY review_date DESC LIMIT ?"
        params.append(limit)
        
        with self.db._get_connection() as conn:
            conn.row_factory = self.db.dict_factory
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_triage_metrics(self, platform=None, time_range='30d'):
        """
        Calculates high-signal metrics for the Triage dashboard.
        """
        days = int(time_range.replace('d', '')) if 'd' in time_range else 30
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = "SELECT rating, sentiment, category FROM filtered_reviews WHERE review_date >= ?"
        params = [since]
        
        if platform and platform.lower() != 'all':
            query += " AND platform = ?"
            params.append(platform.lower())
            
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
        total = len(rows)
        if total == 0:
            return {
                "total_reviews": 0, "avg_rating": 0,
                "rating_distribution": {5:0,4:0,3:0,2:0,1:0},
                "sentiment_split": {"Positive": 0, "Neutral": 0, "Negative": 0},
                "health_breakdown": {"promoters": 0, "passives": 0, "detractors": 0}
            }
            
        ratings = [r[0] for r in rows]
        sentiments = [r[1] for r in rows]
        
        avg_rating = round(sum(ratings) / total, 1)
        r_dist = {i: ratings.count(i) for i in range(1, 6)}
        s_split = {s: sentiments.count(s) for s in ["Positive", "Neutral", "Negative"]}
        
        return {
            "total_reviews": total,
            "avg_rating": avg_rating,
            "rating_distribution": r_dist,
            "sentiment_split": s_split,
            "health_breakdown": {
                "promoters": r_dist.get(5, 0) + r_dist.get(4, 0),
                "passives": r_dist.get(3, 0),
                "detractors": r_dist.get(2, 0) + r_dist.get(1, 0)
            }
        }

    def classify_locally(self, text, rating):
        """
        Simple keyword-based classifier to provide immediate intelligence.
        """
        text = text.lower()
        rules = {
            'App Crash': ['crash', 'close', 'stuck', 'freeze', 'not opening', 'broken'],
            'Performance': ['slow', 'lag', 'loading', 'speed', 'fast', 'hang'],
            'Customer Support': ['support', 'customer care', 'help', 'respond', 'chat', 'ticket'],
            'Charges & Fees': ['fee', 'charge', 'cost', 'brokerage', 'money', 'deduct', 'hidden'],
            'Account Issues': ['login', 'account', 'kyc', 'otp', 'access', 'delete', 'verify'],
            'UX Issues': ['ui', 'ux', 'design', 'interface', 'look', 'confusing', 'hard to use'],
            'Feature Request': ['add', 'wish', 'want', 'please', 'missing', 'feature']
        }
        
        for cat, keywords in rules.items():
            if any(k in text for k in keywords):
                return cat
        
        return 'General Praise' if rating >= 4 else 'General Feedback'

    def sync_live_reviews(self):
        """
        Triggers live ingestion and stores results in the DB with local classification.
        """
        from services.ingestion_service.real_ingestor import RealIngestionService
        ingestor = RealIngestionService()
        
        live_data = ingestor.ingest_all(limit_per_platform=2500)
        
        # Process for sentiment/category
        processed = []
        for r in live_data:
            # Sentiment Logic
            if not r.get('sentiment'):
                r['sentiment'] = 'Positive' if r['rating'] >= 4 else 'Negative' if r['rating'] <= 2 else 'Neutral'
            
            # Classification Logic
            if not r.get('category') or r['category'] == 'Uncategorized':
                r['category'] = self.classify_locally(r['review_text'], r['rating'])

            # Identity Logic (Real Names)
            name = r.get('user_name', 'Anonymous')
            if name == 'A Google user' or not name:
                # Use first 4 chars of content_hash to make it unique but realistic
                text_to_hash = f"{r['review_text']}_{r.get('platform', 'all')}"
                import hashlib
                h = hashlib.md5(text_to_hash.encode()).hexdigest()[:4].upper()
                r['user_name'] = f"Google User #{h}"
            else:
                r['user_name'] = name

            processed.append(r)
            
        self.db.upsert_filtered_reviews(processed)
        return len(processed)

    def get_review_by_id(self, review_id):
        with self.db._get_connection() as conn:
            conn.row_factory = self.db.sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM filtered_reviews WHERE id = ?", (review_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def assign_review(self, review_id, pm_name):
        """
        Assigns a review to a PM and creates a Jira ticket.
        """
        from .jira_service import JiraService
        jira = JiraService()
        
        # 1. Get review data for the ticket
        review_data = self.get_review_by_id(review_id)
        
        # 2. Create Jira Ticket
        jira_id = None
        if review_data:
            jira_id = jira.create_ticket(review_data)
            
        # 3. Update DB
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE filtered_reviews SET assigned_to = ?, jira_id = ? WHERE id = ?",
                (pm_name, jira_id, review_id)
            )
            conn.commit()
            
        return {"assigned_to": pm_name, "jira_id": jira_id}
