from app_store_scraper import AppStore
import logging

logging.basicConfig(level=logging.INFO)

def test_ios_variants():
    variants = [
        {"name": "indmoney-stocks-mutual-funds", "id": 1451296538},
        {"name": "indmoney", "id": 1451296538},
    ]
    
    for v in variants:
        print(f"\nTrying Variant: {v['name']} (ID: {v['id']})")
        try:
            app = AppStore(country='in', app_name=v['name'], app_id=v['id'])
            app.review(how_many=10)
            print(f"SUCCESS! Found {len(app.reviews)} reviews")
            if len(app.reviews) > 0:
                return v
        except Exception as e:
            print(f"FAILED: {e}")
    
    return None

if __name__ == "__main__":
    working = test_ios_variants()
    if working:
        print(f"\nFINAL WORKING CONFIG: {working}")
    else:
        print("\nALL VARIANTS FAILED")
