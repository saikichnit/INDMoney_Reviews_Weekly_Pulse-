import pytest
import asyncio
from aggregation.aggregator import Aggregator

def test_aggregator_merge_strategy():
    aggregator = Aggregator()
    groq_out = {
        "themes": ["Theme A", "Theme B"],
        "summary": "This is a long summary that is over 150 words long. " * 20,
        "action_items": ["Action 1"],
        "quotes": ["Quote 1"]
    }
    gemini_out = {
        "themes": ["Theme B", "Theme C"],
        "summary": "Short summary",
        "action_items": ["Action 2"],
        "quotes": ["Quote 2"]
    }
    
    result = aggregator.aggregate(groq_out, gemini_out)
    
    # Check theme merging and deduplication
    assert "Theme A" in result['themes']
    assert "Theme C" in result['themes']
    assert len(result['themes']) <= 5
    
    # Check summary selection (prefer Groq if long enough)
    assert len(result['summary'].split()) >= 150
    
    # Check action item merging
    assert "Action 1" in result['action_items']
    assert "Action 2" in result['action_items']

def test_aggregator_fallback_strategy():
    aggregator = Aggregator()
    groq_error = {"error": "API Failure"}
    gemini_success = {"themes": ["Gemini Theme"], "summary": "Gemini Summary"}
    
    result = aggregator.aggregate(groq_error, gemini_success)
    assert result['summary'] == "Gemini Summary"
    assert result['themes'] == ["Gemini Theme"]
