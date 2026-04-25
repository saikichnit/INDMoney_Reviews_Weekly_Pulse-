import requests
import json

def debug_rss_v3():
    # NEW ID: 1456108169
    url = "https://itunes.apple.com/in/rss/customerreviews/id=1456108169/sortBy=mostRecent/json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"Fetching: {url}")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            entries = data.get('feed', {}).get('entry', [])
            print(f"Found {len(entries)} entries")
            if len(entries) > 1:
                # index 0 is sometimes app info, index 1+ are reviews
                print(f"Review Sample: {entries[1].get('content', {}).get('label', '')[:100]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_rss_v3()
