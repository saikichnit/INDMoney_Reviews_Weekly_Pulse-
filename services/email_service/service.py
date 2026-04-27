import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

class EmailDeliveryService:
    def __init__(self):
        load_dotenv()
        self.user = os.environ.get("EMAIL_SENDER")
        self.password = os.environ.get("EMAIL_PASSWORD")
        self.host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.environ.get("SMTP_PORT", 587))

    def prepare_email(self, note: dict, themes: list, recipient_name: str = None, fee_scenarios: list = None) -> dict:
        greeting_name = recipient_name if recipient_name else "Stakeholders"
        summary = note.get('summary', '')
        
        # Theme Items HTML
        theme_html = ""
        for t in themes:
            name = t.get('name') if isinstance(t, dict) else t
            percent = t.get('percentage', 'N/A') if isinstance(t, dict) else 'N/A'
            theme_html += f"""
            <div style="padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 10px; background-color: #ffffff;">
                <div style="font-weight: bold; color: #0f172a; font-size: 14px;">{name}</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;">Impact: {percent}%</div>
            </div>
            """

        # Quotes HTML
        quotes_html = "".join([f'<div style="font-style: italic; color: #475569; border-left: 3px solid #0066CC; padding-left: 15px; margin-bottom: 15px; font-size: 13px;">"{q}"</div>' for q in note.get('quotes', [])])
        
        # Actions HTML
        actions_html = "".join([f'<li style="margin-bottom: 10px; color: #1e293b;">{a}</li>' for a in note.get('action_items', [])])

        # Education HTML
        education_html = ""
        if fee_scenarios:
            education_html = '<div style="margin-bottom: 30px; border: 1px solid #bae6fd; background-color: #f0f9ff; padding: 20px; border-radius: 10px;">'
            education_html += '<h2 style="font-size: 12px; font-weight: bold; color: #0369a1; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 15px;">🎓 Proactive Financial Education</h2>'
            for fee in fee_scenarios[:2]:
                bullets = "".join([f'<div style="margin-bottom: 6px;">• {b}</div>' for b in fee.get('explanation_bullets', [])[:2]])
                source = f'<div style="margin-top: 8px;"><a href="{fee.get("source_links")[0]}" style="color: #0369a1; font-size: 11px; text-decoration: underline;">Read Official Source</a></div>' if fee.get('source_links') else ""
                education_html += f"""
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: bold; color: #0c4a6e; font-size: 14px; margin-bottom: 6px;">{fee.get('scenario_name')}</div>
                    <div style="font-size: 13px; color: #334155; line-height: 1.5;">{bullets}</div>
                    {source}
                </div>
                """
            education_html += '</div>'

        html_body = f"""
        <html>
        <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #334155;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <!-- Banner Image -->
                <img src="cid:executive_banner" style="width: 100%; height: auto; display: block;" />
                
                <div style="padding: 30px;">
                    <div style="margin-bottom: 30px;">
                        <h1 style="font-size: 20px; font-weight: bold; color: #0f172a; margin-bottom: 10px;">Executive Intelligence Pulse</h1>
                        <p style="font-size: 14px; color: #64748b; line-height: 1.6;">Hi {greeting_name}, here is the strategic synthesis of recent user feedback and product performance signals.</p>
                    </div>

                    <div style="margin-bottom: 30px; background-color: #f1f5f9; padding: 20px; border-radius: 10px;">
                        <h2 style="font-size: 12px; font-weight: bold; color: #0066CC; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px;">Executive Summary</h2>
                        <div style="font-size: 15px; line-height: 1.6; color: #1e293b; font-weight: 500;">{summary}</div>
                    </div>

                    {education_html}

                    <div style="margin-bottom: 30px;">
                        <h2 style="font-size: 12px; font-weight: bold; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 15px;">Strategic Themes</h2>
                        {theme_html}
                    </div>

                    <div style="margin-bottom: 30px;">
                        <h2 style="font-size: 12px; font-weight: bold; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 15px;">Golden User Quotes</h2>
                        {quotes_html}
                    </div>

                    <div style="margin-bottom: 30px;">
                        <h2 style="font-size: 12px; font-weight: bold; color: #0066CC; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 15px;">Recommended Action Items</h2>
                        <ul style="font-size: 14px; line-height: 1.6; padding-left: 20px; margin: 0;">
                            {actions_html}
                        </ul>
                    </div>

                    <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; text-align: center;">
                        <p style="font-size: 12px; color: #94a3b8; font-style: italic;">A high-fidelity PDF report and raw JSON data are attached for deep-dive analysis.</p>
                        <div style="margin-top: 15px;">
                            <span style="font-size: 10px; font-weight: bold; color: #ffffff; background-color: #0066CC; padding: 6px 12px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.05em;">INDPlus Professional</span>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        return {
            "subject": f"INDPlus Strategic Pulse - {current_date}",
            "body": html_body
        }

    def deliver(self, recipient_email: str, subject: str, body: str, attachment_path: str = None):
        if not self.user or not self.password:
            print("ERROR: Email credentials not configured.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Attach HTML Body
            msg.attach(MIMEText(body, 'html'))

            # Attach Banner Image (CID)
            banner_path = os.environ.get("EMAIL_BANNER_PATH")
            if not banner_path or not os.path.exists(banner_path):
                # Fallback to local project path
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                banner_path = os.path.join(project_root, "assets", "banner.png")

            if os.path.exists(banner_path):
                from email.mime.image import MIMEImage
                with open(banner_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', '<executive_banner>')
                    img.add_header('Content-Disposition', 'inline', filename='banner.png')
                    msg.attach(img)

            # Handle PDF Attachment
            if attachment_path and os.path.exists(attachment_path):
                from email.mime.base import MIMEBase
                from email import encoders
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}",
                )
                msg.attach(part)
                print(f"DEBUG: Attached file {attachment_path}")

            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"SUCCESS: Executive HTML Email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"ERROR: SMTP failure: {e}")
            return False
