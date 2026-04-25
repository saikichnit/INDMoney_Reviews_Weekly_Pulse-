from google_play_scraper import reviews, Sort
from app_store_scraper import AppStore
from datetime import datetime, timedelta

def test_ingest():
    # Android
    print("Testing Android...")
    result, _ = reviews(
        "com.indigo.wealth",
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=10
    )
    print(f"Android found: {len(result)}")
    
    # iOS
    print("Testing iOS...")
    try:
        app = AppStore(country='in', app_name='indmoney', app_id=1453186895)
        app.review(how_many=10)
        print(f"iOS found: {len(app.reviews)}")
    except Exception as e:
        print(f"iOS Error: {e}")

if __name__ == "__main__":
    test_ingest()
