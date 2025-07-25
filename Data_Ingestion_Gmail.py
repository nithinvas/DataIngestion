import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

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
        if part['mimeType'] == 'text/html':
            data = part['body']['data']
            decoded = base64.urlsafe_b64decode(data).decode('utf-8')
            soup = BeautifulSoup(decoded, 'html.parser')
            return soup.get_text()
    return "[No readable content]"

if __name__ == '__main__':
    service = authenticate()
    receipts = fetch_receipts(service)

    print(f"Found {len(receipts)} receipt-like emails.\n")
    for msg in receipts[:3]:
        print("==========")
        print(extract_text(service, msg['id']))
