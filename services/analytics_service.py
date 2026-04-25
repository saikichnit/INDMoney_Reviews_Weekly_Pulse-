from storage.db import DatabaseManager
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self):
        self.db = DatabaseManager()

    def get_full_analytics(self, time_range='30d'):
        """
        Returns a unified intelligence payload combining core metrics and category deep-dives.
        """
        days = int(time_range.replace('d', '')) if 'd' in time_range else 30
        since = (datetime.now() - timedelta(days=days)).isoformat()

        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Core KPIs
            cursor.execute("SELECT COUNT(*), AVG(rating) FROM filtered_reviews WHERE review_date >= ?", (since,))
            total, avg = cursor.fetchone()
            total = total or 0
            avg = round(avg or 0, 1)
            
            # 2. Sentiment Splits
            cursor.execute("SELECT sentiment, COUNT(*) FROM filtered_reviews WHERE review_date >= ? GROUP BY sentiment", (since,))
            s_counts = dict(cursor.fetchall())
            pos = s_counts.get('Positive', 0)
            neg = s_counts.get('Negative', 0)
            neu = s_counts.get('Neutral', 0)
            
            # 3. Rating Dist (NPS)
            cursor.execute("SELECT rating, COUNT(*) FROM filtered_reviews WHERE review_date >= ? GROUP BY rating", (since,))
            r_dist = {str(r): c for r, c in cursor.fetchall()}
            
            # 4. Unified Category Intelligence (Combined Metrics)
            cursor.execute("""
                SELECT 
                    category, 
                    COUNT(*) as total_signals,
                    AVG(rating) as avg_rating,
                    SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) as pos_count,
                    SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END) as neg_count
                FROM filtered_reviews 
                WHERE review_date >= ? AND category != 'Uncategorized'
                GROUP BY category 
                ORDER BY total_signals DESC
            """, (since,))
            
            categories_intelligence = []
            for row in cursor.fetchall():
                cat, count, c_avg, c_pos, c_neg = row
                categories_intelligence.append({
                    "name": cat,
                    "count": count,
                    "avg_rating": round(c_avg or 0, 1),
                    "pos_p": round((c_pos/count * 100), 1) if count > 0 else 0,
                    "neg_p": round((c_neg/count * 100), 1) if count > 0 else 0,
                    "health": "Good" if (c_avg or 0) >= 4.0 else "Critical" if (c_avg or 0) < 3.0 else "Needs Attention"
                })
            
            # 5. Trend Analysis
            cursor.execute("""
                SELECT date(review_date) as d, sentiment, COUNT(*) 
                FROM filtered_reviews WHERE review_date >= ? 
                GROUP BY d, sentiment ORDER BY d ASC
            """, (since,))
            
            trend_map = {}
            for d, s, c in cursor.fetchall():
                if d not in trend_map:
                    trend_map[d] = {"date": d, "positive": 0, "negative": 0, "neutral": 0}
                if s and s.lower() in trend_map[d]:
                    trend_map[d][s.lower()] = c

            return {
                "summary": {
                    "total_reviews": total,
                    "avg_rating": avg,
                    "sentiment": {
                        "positive": pos,
                        "negative": neg,
                        "neutral": neu,
                        "pos_p": round((pos/total * 100), 1) if total > 0 else 0,
                        "neg_p": round((neg/total * 100), 1) if total > 0 else 0,
                        "neu_p": round((neu/total * 100), 1) if total > 0 else 0
                    }
                },
                "nps": {
                    "promoters": r_dist.get('5', 0) + r_dist.get('4', 0),
                    "passives": r_dist.get('3', 0),
                    "detractors": r_dist.get('2', 0) + r_dist.get('1', 0)
                },
                "categories": categories_intelligence,
                "trends": list(trend_map.values())
            }
