from datetime import datetime, timedelta

class AnalyticsEngine:
    def __init__(self, db_manager):
        self.db = db_manager

    def compute_theme_sentiment(self, reviews: list, theme: str) -> float:
        # Simple heuristic sentiment scoring for Phase 3
        # In production, this would use a dedicated sentiment model
        pos_words = {'good', 'great', 'love', 'amazing', 'fast', 'easy'}
        neg_words = {'slow', 'bad', 'crash', 'issue', 'hate', 'difficult'}
        
        relevant_reviews = [r for r in reviews if theme.lower() in r['review_text'].lower()]
        if not relevant_reviews: return 0.0
        
        scores = []
        for r in relevant_reviews:
            text = r['review_text'].lower()
            pos_count = sum(1 for w in pos_words if w in text)
            neg_count = sum(1 for w in neg_words if w in text)
            score = (pos_count - neg_count) / max(1, pos_count + neg_count)
            scores.append(score)
            
        return sum(scores) / len(scores)

    def get_weekly_trends(self):
        # Fetch last 2 reports and compare
        reports = self.db.get_all_reports()
        if len(reports) < 2:
            return {"trend": "Insufficient data", "change": 0}
        
        current = reports[0]['review_count']
        previous = reports[1]['review_count']
        change = ((current - previous) / previous) * 100 if previous > 0 else 0
        
        return {
            "current_volume": current,
            "previous_volume": previous,
            "volume_change_pct": round(change, 1),
            "status": "Increased" if change > 0 else "Decreased"
        }
