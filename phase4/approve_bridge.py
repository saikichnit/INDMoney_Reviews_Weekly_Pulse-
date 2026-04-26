import sys
import os
import json
import argparse
from datetime import datetime

# Add root directory to path for service imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services
from storage.db import DatabaseManager
from services.pdf_service.service import PDFService
from services.email_service.service import EmailDeliveryService
from services.mcp_service.google_docs_helper import GoogleDocsHelper

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, type=int)
    parser.add_argument("--text", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--mode", choices=["email", "docs", "both"], default="both")
    args = parser.parse_args()

    # Database
    db = DatabaseManager()
    report = db.get_report_by_id(args.id)
    if not report:
        print(json.dumps({"error": f"Report ID {args.id} not found in database"}))
        sys.exit(1)

    # Use the edited text from the UI
    report['summary'] = args.text

    results = {"id": args.id}

    # 1. Google Docs Sync (Append)
    if args.mode in ["docs", "both"]:
        try:
            docs_helper = GoogleDocsHelper()
            docs_success = docs_helper.append_report(args.text)
            results["docs"] = docs_success
        except Exception as e:
            results["docs"] = False
            results["docs_error"] = str(e)

    # 2. PDF & Email
    if args.mode in ["email", "both"]:
        try:
            # Generate PDF
            pdf_service = PDFService()
            pdf_path = pdf_service.generate_report_pdf(
                report, 
                report['themes'], 
                report.get('fee_scenarios', [])
            )
            results["pdf_path"] = pdf_path
            
            # Prepare & Deliver Email
            email_service = EmailDeliveryService()
            email_content = email_service.prepare_email(
                report, 
                report['themes'], 
                recipient_name=args.email.split('@')[0],
                fee_scenarios=report.get('fee_scenarios', [])
            )
            
            email_success = email_service.deliver(
                args.email, 
                email_content['subject'], 
                email_content['body'], 
                attachment_path=pdf_path
            )
            results["email"] = email_success
        except Exception as e:
            results["email"] = False
            results["email_error"] = str(e)

    print(json.dumps(results))

if __name__ == "__main__":
    main()
