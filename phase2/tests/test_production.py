import pytest
import os
import sys
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.join(os.getcwd(), 'phase2'))

from services.preprocessing_service.service import PreprocessingService
from storage.db import DatabaseManager

@pytest.fixture
def db():
    return DatabaseManager(db_path="data/test_pulse.db")

@pytest.fixture
def preprocessor(db):
    return PreprocessingService(db, min_words=5)

def test_preprocessing_filters_short_reviews(preprocessor):
    reviews = [
        {"review_text": "Good", "rating": 5, "date": "2024-01-01"},
        {"review_text": "This is a very good app indeed.", "rating": 5, "date": "2024-01-02"}
    ]
    filtered = preprocessor.process(reviews)
    assert len(filtered) == 1
    assert filtered[0]['review_text'] == "This is a very good app indeed."

def test_preprocessing_removes_pii(preprocessor):
    reviews = [
        {"review_text": "Contact me at test@example.com please.", "rating": 5, "date": "2024-01-01"}
    ]
    filtered = preprocessor.process(reviews)
    assert "[EMAIL]" in filtered[0]['review_text']

from services.email_service.service import EmailDeliveryService

@pytest.fixture
def email_service():
    return EmailDeliveryService()

def test_email_personalization(email_service):
    note = {"summary": "Sum", "quotes": ["Q"], "action_items": ["A"]}
    themes = ["Theme"]
    
    # Test with name
    email = email_service.prepare_email(note, themes, recipient_name="Sai")
    assert "Hi Sai," in email['body']
    assert "Thanks," in email['body']
    assert "INDMoney Team" in email['body']
    
    # Test fallback
    email_fallback = email_service.prepare_email(note, themes)
    assert "Hi there," in email_fallback['body']

def test_db_storage(db):
    report_data = {
        "summary": "Test Summary",
        "themes": ["Theme 1"],
        "quotes": ["Quote 1"],
        "action_items": ["Action 1"],
        "email_draft": {"subject": "Sub", "body": "Body"}
    }
    rid = db.save_report(report_data, 10)
    report = db.get_report_by_id(rid)
    assert report['summary'] == "Test Summary"
    assert report['review_count'] == 10
