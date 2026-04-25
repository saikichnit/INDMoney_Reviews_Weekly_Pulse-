import re
from langdetect import detect, DetectorFactory

# Ensure reproducible results from langdetect
DetectorFactory.seed = 0

class Processor:
    def __init__(self, min_words: int = 5):
        self.min_words = min_words
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        self.id_pattern = re.compile(r'\b\d{8,}\b')

    def is_english(self, text: str) -> bool:
        try:
            return detect(text) == 'en'
        except:
            return False

    def sanitize(self, text: str) -> str:
        if not text: return ""
        text = self.email_pattern.sub("[EMAIL]", text)
        text = self.phone_pattern.sub("[PHONE]", text)
        text = self.id_pattern.sub("[ID]", text)
        return " ".join(text.split())

    def filter_short_reviews(self, reviews: list) -> list:
        """Utility to filter out reviews below the minimum word threshold."""
        return [r for r in reviews if len(r.get('review_text', '').split()) >= self.min_words]

    def filter_non_english_reviews(self, reviews: list) -> list:
        """Utility to keep only English reviews."""
        return [r for r in reviews if self.is_english(r.get('review_text', ''))]

    def process_batch(self, reviews: list) -> list:
        # 1. Word Count Filter (Strict Removal)
        reviews = self.filter_short_reviews(reviews)
        
        # 2. Language Filtering (English Only)
        reviews = self.filter_non_english_reviews(reviews)
        
        processed = []
        for r in reviews:
            # 3. PII Removal
            r['review_text'] = self.sanitize(r['review_text'])
            processed.append(r)
            
        return processed
