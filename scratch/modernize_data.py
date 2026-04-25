import json
import os
from datetime import datetime, timedelta
import random

def modernize_data():
    file_path = "data/raw/stress_test_1000.json"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"🔄 Modernizing {file_path} for real-time dashboard testing...")
    
    with open(file_path, 'r') as f:
        data = json.load(f)

    now = datetime.now()
    
    for i, item in enumerate(data):
        # Distribute reviews over the last 360 days
        days_ago = random.randint(0, 400)
        new_date = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        item['date'] = new_date.isoformat()
        
        # Add platform if missing
        if 'platform' not in item:
            item['platform'] = random.choice(['Android', 'iOS'])

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"✅ Successfully modernized {len(data)} reviews. Range: Last 400 days.")

if __name__ == "__main__":
    modernize_data()
