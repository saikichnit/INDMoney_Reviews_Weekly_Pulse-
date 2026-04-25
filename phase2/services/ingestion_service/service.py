import os
import pandas as pd
import hashlib
from typing import List, Dict

class IngestionService:
    def __init__(self, db_manager, max_reviews: int = 1000):
        self.db = db_manager
        self.max_reviews = max_reviews

    def _get_hash(self, text: str) -> str:
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    def fetch_from_local(self, folder_path: str, limit: int = None, days: int = 60) -> List[Dict]:
        max_limit = limit if limit is not None else self.max_reviews
        files = [f for f in os.listdir(folder_path) if f.endswith(('.csv', '.json'))]
        all_reviews = []
        
        for f_name in files:
            path = os.path.join(folder_path, f_name)
            ext = os.path.splitext(f_name)[1].lower()
            
            try:
                if ext == '.csv':
                    df = pd.read_csv(path)
                else:
                    df = pd.read_json(path)
                
                # Platform Detection
                platform = "Universal"
                if "ios" in f_name.lower() or "apple" in f_name.lower() or "app_store" in f_name.lower():
                    platform = "iOS"
                elif "android" in f_name.lower() or "play" in f_name.lower():
                    platform = "Android"

                # Normalize
                mapping = {
                    'rating': ['rating', 'stars', 'score'],
                    'review_text': ['review_text', 'content', 'text', 'review'],
                    'date': ['date', 'timestamp', 'created_at']
                }

                for _, row in df.iterrows():
                    item = {}
                    for target, sources in mapping.items():
                        val = next((row[src] for src in sources if src in row), "")
                        item[target] = str(val)
                    
                    # Manual platform override if column exists
                    item['platform'] = row.get('platform', platform)

                    if item['review_text']:
                        item['hash'] = self._get_hash(item['review_text'])
                        all_reviews.append(item)
            except Exception as e:
                print(f"Error loading {f_name}: {e}")

        # Apply day-based filter if requested
        if days > 0:
            from datetime import datetime, timedelta
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            all_reviews = [r for r in all_reviews if r.get('date', '') >= cutoff]

        # Sort and Cap
        all_reviews.sort(key=lambda x: x.get('date', ''), reverse=True)
        latest_reviews = all_reviews[:max_limit]
        
        # Save to Raw Storage
        self.db.save_raw_reviews(latest_reviews)
        
        return latest_reviews
