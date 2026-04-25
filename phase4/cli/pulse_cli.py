import argparse
import sys
import os

# Add project root to path for api-client import
sys.path.append(os.getcwd())
from phase4.api_client.client import PulseAPIClient

client = PulseAPIClient()

def main():
    parser = argparse.ArgumentParser(description="INDMoney Review Pulse CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Generate Report
    gen_parser = subparsers.add_parser("generate-report")
    gen_parser.add_argument("--name", help="Recipient name for personalization")
    gen_parser.add_argument("--max-reviews", type=int, default=1000, help="Max reviews to process")
    gen_parser.add_argument("--weeks", type=int, default=8, help="Time window in weeks")

    # List Reports
    subparsers.add_parser("list-reports")

    # Send Email
    email_parser = subparsers.add_parser("send-email")
    email_parser.add_argument("--id", required=True, type=int, help="Report ID to send")
    email_parser.add_argument("--name", required=True, help="Recipient name")
    email_parser.add_argument("--email", required=True, help="Recipient email")

    args = parser.parse_args()

    if args.command == "generate-report":
        res = client.generate_report(args.name, args.max_reviews, args.weeks)
        print(f"SUCCESS: Report #{res.get('report_id')} generated.")
        
    elif args.command == "list-reports":
        reports = client.list_reports()
        print(f"{'ID':<5} | {'Date':<15} | {'Count':<5}")
        print("-" * 30)
        for r in reports:
            print(f"{r['id']:<5} | {r['created_at'][:10]:<15} | {r['review_count']:<5}")

    elif args.command == "send-email":
        res = client.send_email(args.id, args.name, args.email)
        print(res.get("message", "Email operation completed."))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
