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
        
        reports_list = db.get_all_reports()
        
        with open("data/latest_pulse.json", "w") as f:
            json.dump(latest_data, f, indent=2)
        with open("data/reports_archive.json", "w") as f:
            json.dump(reports_list, f, indent=2)
            
        print(json.dumps({"report_id": report_id, "status": "success"}))
    else:
        print(json.dumps({"error": "Pipeline failed to generate report"}))

if __name__ == "__main__":
    main()
