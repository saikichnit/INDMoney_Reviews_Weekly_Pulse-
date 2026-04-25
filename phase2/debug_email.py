import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'phase2'))

from services.email_service.service import EmailDeliveryService
from dotenv import load_dotenv

load_dotenv()
mailer = EmailDeliveryService()

# Create a test file
test_file = "test_attachment_debug.txt"
with open(test_file, "w") as f:
    f.write("This is a debug attachment for INDMoney.")

# Send test email
success = mailer.deliver(
    recipient_email="chsk.nitw@gmail.com",
    subject="INDMoney Debug: Attachment Test",
    body="Please check if this email has a text file attachment.",
    attachment_path=test_file
)

print(f"DEBUG_SEND_STATUS: {success}")
if os.path.exists(test_file):
    os.remove(test_file)
