import sys
import os
import json
import argparse
from datetime import datetime

# Add root directory to path for service imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.intelligence_orchestrator import IntelligenceOrchestrator
from storage.db import DatabaseManager

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--max_reviews", type=int, default=1000)
    args = parser.parse_args()

    # Use the same production DB as Streamlit
    db_path = "data/pulse_production.db"
    orchestrator = IntelligenceOrchestrator(db_path=db_path)
    
    # Run Pipeline
    report_id, payload = orchestrator.run_pipeline(
        max_reviews=args.max_reviews,
        days=args.days
    )

    if report_id:
        # Also update the latest_pulse.json for the frontend
        db = DatabaseManager(db_path)
        with db._get_connection() as conn:
            import pandas as pd
            sample_reviews = pd.read_sql_query("SELECT user_name, review_text, rating, platform, review_date, category, sentiment FROM filtered_reviews ORDER BY review_date DESC LIMIT 5000", conn).to_dict('records')
        
        latest_data = {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat(),
            "payload": payload,
            "reviews": sample_reviews
        }
        
        # Persistence logic for GitHub Environments (where SQLite is transient)
        reports_archive_path = "data/reports_archive.json"
        existing_archive = []
        if os.path.exists(reports_archive_path):
            try:
                with open(reports_archive_path, 'r') as f:
                    existing_archive = json.load(f)
            except:
                existing_archive = []
        
        # Merge DB reports with JSON archive (deduplicate by created_at or id)
        db_reports = db.get_all_reports()
        
        # Simple merge: Add new DB reports to existing archive if they don't exist
        existing_ids = {r.get('id') for r in existing_archive if r.get('id')}
        for dr in db_reports:
            if dr.get('id') not in existing_ids:
                existing_archive.insert(0, dr)
        
        # Sort by creation date descending
        existing_archive.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        with open("data/latest_pulse.json", "w") as f:
            json.dump(latest_data, f, indent=2)
            
        with open(reports_archive_path, "w") as f:
            json.dump(existing_archive, f, indent=2)
            
        print(json.dumps({"report_id": report_id, "status": "success"}))
    else:
        print(json.dumps({"error": "Pipeline failed to generate report"}))

if __name__ == "__main__":
    main()
