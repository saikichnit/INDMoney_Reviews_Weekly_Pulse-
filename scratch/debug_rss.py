import requests
import json

def debug_rss():
    url = "https://itunes.apple.com/in/rss/customerreviews/id=1451296538/json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Fetching: {url}")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        if response.status_code == 200:
            data = response.json()
            entries = data.get('feed', {}).get('entry', [])
            print(f"Found {len(entries)} entries")
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_rss()
