import requests
import json

def test_rss_groww():
    # Groww ID: 1318353009
    url = "https://itunes.apple.com/in/rss/customerreviews/id=1318353009/sortBy=mostRecent/json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"Fetching Groww RSS: {url}")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            entries = data.get('feed', {}).get('entry', [])
            print(f"Found {len(entries)} entries")
            if len(entries) > 1:
                print(f"Review Sample: {entries[1].get('content', {}).get('label', '')[:100]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rss_groww()
