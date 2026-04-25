import requests
import json

def debug_rss_v2():
    # Variant 1: mostRecent
    url1 = "https://itunes.apple.com/in/rss/customerreviews/id=1451296538/sortBy=mostRecent/json"
    # Variant 2: default
    url2 = "https://itunes.apple.com/in/rss/customerreviews/id=1451296538/json"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    for url in [url1, url2]:
        print(f"\nFetching: {url}")
        try:
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                entries = data.get('feed', {}).get('entry', [])
                print(f"Found {len(entries)} entries")
                if len(entries) > 0:
                    print(f"First entry sample: {entries[0].get('content', {}).get('label', '')[:50]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_rss_v2()
