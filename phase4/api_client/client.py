import requests

class PulseAPIClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url

    def generate_report(self, recipient_name=None, max_reviews=1000, weeks=8):
        url = f"{self.base_url}/api/generate-report"
        params = {
            "recipient_name": recipient_name,
            "max_reviews": max_reviews,
            "weeks": weeks
        }
        response = requests.post(url, params=params)
        return response.json()

    def list_reports(self):
        url = f"{self.base_url}/api/reports"
        response = requests.get(url)
        return response.json()

    def get_report(self, report_id):
        url = f"{self.base_url}/api/reports/{report_id}"
        response = requests.get(url)
        return response.json()

    def send_email(self, report_id, name, email):
        url = f"{self.base_url}/api/send-email/{report_id}"
        params = {"recipient_email": email}
        # Note: Name personalization is handled at the generation stage in our current Phase 2 architecture
        response = requests.post(url, params=params)
        return response.json()
