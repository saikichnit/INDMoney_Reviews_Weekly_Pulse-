import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

class GoogleDocsHelper:
    def __init__(self):
        load_dotenv()
        self.doc_id = os.environ.get("GOOGLE_DOC_ID")
        self.creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.scopes = ['https://www.googleapis.com/auth/documents']

    def sync_report(self, text: str) -> bool:
        """
        Clears the document and syncs the specific report text for standalone archival.
        """
        try:
            # Try loading from Environment Variable (GitHub Actions/Vercel)
            try:
                env_creds = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
                if env_creds:
                    creds_dict = json.loads(env_creds)
                    creds = service_account.Credentials.from_service_account_info(
                        creds_dict, scopes=self.scopes)
                else:
                    raise ImportError
            except (ImportError, KeyError, Exception):
                # Try loading from Streamlit Secrets first (Production/Cloud)
                try:
                    import streamlit as st
                    if "GCP_SERVICE_ACCOUNT" in st.secrets:
                        creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
                        creds = service_account.Credentials.from_service_account_info(
                            creds_dict, scopes=self.scopes)
                    else:
                        raise ImportError
                except (ImportError, KeyError, Exception):
                    # Fallback to local file (Development)
                    if not self.creds_file or not os.path.exists(self.creds_file):
                        print(f"ERROR: Credentials file not found: {self.creds_file}")
                        return False
                    creds = service_account.Credentials.from_service_account_file(
                        self.creds_file, scopes=self.scopes)
            
            service = build('docs', 'v1', credentials=creds)

            # 1. Get document length to clear it
            doc = service.documents().get(documentId=self.doc_id).execute()
            content = doc.get('body').get('content')
            end_index = content[-1].get('endIndex')

            requests = []
            
            # 2. Clear entire document if it has content (min length is 2)
            if end_index > 2:
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index - 1
                        }
                    }
                })

            # 3. Insert standalone report text
            requests.append({
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': text
                }
            })

            service.documents().batchUpdate(
                documentId=self.doc_id, body={'requests': requests}).execute()
            
            print(f"SUCCESS: Standalone report synced to Google Doc {self.doc_id}")
            return True
        except Exception as e:
            print(f"ERROR: Google Docs update failed: {e}")
            return False

    def append_report(self, text: str) -> bool:
        """
        Appends the report text to the end of the document with a timestamp header.
        """
        try:
            # Try loading from Environment Variable (GitHub Actions/Vercel)
            try:
                env_creds = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
                if env_creds:
                    creds_dict = json.loads(env_creds)
                    creds = service_account.Credentials.from_service_account_info(
                        creds_dict, scopes=self.scopes)
                else:
                    raise ImportError
            except (ImportError, KeyError, Exception):
                # Try loading from Streamlit Secrets first
                try:
                    import streamlit as st
                    if "GCP_SERVICE_ACCOUNT" in st.secrets:
                        creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
                        creds = service_account.Credentials.from_service_account_info(
                            creds_dict, scopes=self.scopes)
                    else:
                        raise ImportError
                except (ImportError, KeyError, Exception):
                    if not self.creds_file or not os.path.exists(self.creds_file):
                        print(f"ERROR: Credentials file not found: {self.creds_file}")
                        return False
                    creds = service_account.Credentials.from_service_account_file(
                        self.creds_file, scopes=self.scopes)
            
            service = build('docs', 'v1', credentials=creds)

            # 1. Get document length
            doc = service.documents().get(documentId=self.doc_id).execute()
            content = doc.get('body').get('content')
            end_index = content[-1].get('endIndex') - 1

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            header = f"\n\n--- INDPlus Intelligence Pulse ({timestamp}) ---\n\n"
            
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': end_index,
                        },
                        'text': header + text
                    }
                }
            ]

            service.documents().batchUpdate(
                documentId=self.doc_id, body={'requests': requests}).execute()
            
            print(f"SUCCESS: Report appended to Google Doc {self.doc_id}")
            return True
        except Exception as e:
            print(f"ERROR: Google Docs append failed: {e}")
            return False
