import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import io
from PyPDF2 import PdfReader

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def fetch_receipts(service):
    results = service.users().messages().list(userId='me', q='subject:receipt OR subject:order OR subject:invoice').execute()
    return results.get('messages', [])

def extract_text(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message.get('payload', {})
    parts = payload.get('parts', [])

    for part in parts:
        data = part['body'].get('data')
        if data:
            try:
                decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
                return decoded
            except Exception as e:
                return f"[Error decoding part: {e}]"
    return "[No readable content]"
      

if __name__ == '__main__':
    service = authenticate()
    receipts = fetch_receipts(service)

    print(f"Found {len(receipts)} receipt-like emails.\n")
    if receipts:
        # Get the least recently received mail (oldest)
        first_msg = receipts[-1]  # Gmail API returns most recent first
        msg_detail = service.users().messages().get(userId='me', id=first_msg['id'], format='full').execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '[No Subject]')
        print("==========")
        print(f"Subject of least recently received mail: {subject}")
        print("Extracted content:")
        print(extract_text(service, first_msg['id']))
