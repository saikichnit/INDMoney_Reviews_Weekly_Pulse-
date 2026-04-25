import re
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

class PreprocessingService:
    def __init__(self, db_manager, min_words: int = 5):
        self.db = db_manager
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
        text = self.email_pattern.sub("[EMAIL]", text)
        text = self.phone_pattern.sub("[PHONE]", text)
        text = self.id_pattern.sub("[ID]", text)
        return " ".join(text.split())

    def process(self, reviews: list) -> list:
        filtered = []
        for r in reviews:
            text = r['review_text']
            
            # 1. Word Count Filter
            if len(text.split()) < self.min_words:
                continue
                
            # 2. Language Filter
            if not self.is_english(text):
                continue
            
            # 3. PII Masking
            r['review_text'] = self.sanitize(text)
            filtered.append(r)
            
        # Save to Filtered Storage
        self.db.save_filtered_reviews(filtered)
        
        return filtered
