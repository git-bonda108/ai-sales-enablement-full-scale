import os
import base64
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

class GmailClient:
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.send'
        ]
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        # Token file stores the user's access and refresh tokens
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def get_unread_emails(self, max_results=10):
        """Get unread emails from inbox"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()

                email_data = self._parse_email(msg)
                emails.append(email_data)

            return emails
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []

    def _parse_email(self, message):
        """Parse email message into structured data"""
        payload = message['payload']
        headers = payload.get('headers', [])

        # Extract headers
        email_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': '',
            'from': '',
            'to': '',
            'date': '',
            'body': ''
        }

        for header in headers:
            name = header['name'].lower()
            if name == 'subject':
                email_data['subject'] = header['value']
            elif name == 'from':
                email_data['from'] = header['value']
            elif name == 'to':
                email_data['to'] = header['value']
            elif name == 'date':
                email_data['date'] = header['value']

        # Extract body
        email_data['body'] = self._get_body(payload)

        return email_data

    def _get_body(self, payload):
        """Extract body from email payload"""
        body = ''

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(
                payload['body']['data']).decode('utf-8')

        return body

    def send_email(self, to, subject, body, thread_id=None):
        """Send an email"""
        try:
            message = {
                'raw': base64.urlsafe_b64encode(
                    f"To: {to}\nSubject: {subject}\n\n{body}".encode()
                ).decode()
            }

            if thread_id:
                message['threadId'] = thread_id

            sent = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            return sent
        except Exception as e:
            print(f"Error sending email: {e}")
            return None

    def mark_as_read(self, message_id):
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking as read: {e}")
            return False
