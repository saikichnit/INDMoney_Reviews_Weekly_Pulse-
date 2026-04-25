import pytest
from ingestion.ingestor import Ingestor
from preprocessing.processor import Processor
import pandas as pd
import os

def test_ingestor_title_removal():
    ingestor = Ingestor()
    data = {'rating': [5], 'title': ['Great App'], 'review_text': ['This is a test review with enough words.'], 'date': ['2024-03-01']}
    df = pd.DataFrame(data)
    normalized = ingestor.normalize_reviews(df)
    assert 'title' not in normalized[0]
    assert normalized[0]['review_text'] == 'This is a test review with enough words.'

def test_processor_min_word_count():
    processor = Processor()
    reviews = [
        {'review_text': 'Short', 'rating': 5},
        {'review_text': 'This review has more than five words in it.', 'rating': 5}
    ]
    processed = processor.process_batch(reviews)
    assert len(processed) == 1
    assert processed[0]['review_text'] == 'This review has more than five words in it.'

def test_processor_language_filter():
    processor = Processor()
    reviews = [
        {'review_text': 'This is an English review for testing.', 'rating': 5},
        {'review_text': 'Ceci est une revue en français.', 'rating': 5} # French
    ]
    processed = processor.process_batch(reviews)
    assert len(processed) == 1
    assert 'English' in processed[0]['review_text']

def test_processor_pii_removal():
    processor = Processor()
    reviews = [{'review_text': 'Contact me at test@example.com or 9876543210', 'rating': 5}]
    processed = processor.process_batch(reviews)
    text = processed[0]['review_text']
    assert '[EMAIL]' in text
    assert '[PHONE]' in text
