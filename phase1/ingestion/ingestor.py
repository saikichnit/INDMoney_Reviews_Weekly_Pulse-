import pandas as pd
import hashlib
import os
import json
from typing import List, Dict

class Ingestor:
    def __init__(self, max_reviews: int = 1000):
        self.max_reviews = max_reviews

    def get_content_hash(self, text: str) -> str:
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    def normalize_reviews(self, df: pd.DataFrame) -> List[Dict]:
        # Mapping for core fields
        mapping = {
            'rating': ['rating', 'stars', 'score'],
            'review_text': ['review_text', 'content', 'text', 'review'],
            'date': ['date', 'timestamp', 'created_at']
        }

        # 1. First, normalize the date column to allow sorting
        # We find which column is the date column
        date_col = next((col for col in ['date', 'timestamp', 'created_at'] if col in df.columns), None)
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            # 2. Sort by date descending (latest first)
            df = df.sort_values(by=date_col, ascending=False)

        normalized = []
        seen_hashes = set()

        for _, row in df.iterrows():
            if len(normalized) >= self.max_reviews:
                break

            item = {}
            for target, sources in mapping.items():
                val = next((row[src] for src in sources if src in row), "")
                # Format date back to string if it was converted
                if target == 'date' and isinstance(val, pd.Timestamp):
                    val = val.strftime('%Y-%m-%d %H:%M:%S')
                item[target] = str(val)

            # Deduplication
            if not item['review_text']:
                continue
                
            r_hash = self.get_content_hash(item['review_text'])
            if r_hash in seen_hashes:
                continue
            
            seen_hashes.add(r_hash)
            normalized.append(item)

        return normalized

    def load_from_file(self, file_path: str) -> List[Dict]:
        if not os.path.exists(file_path):
            return []
        
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext == '.json':
                df = pd.read_json(file_path)
            else:
                return []
            return self.normalize_reviews(df)
        except Exception:
            return []
