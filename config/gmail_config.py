import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly']

class GmailIntegration:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate using the credentials.json file"""
        creds = None

        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=8080)
                else:
                    st.error("❌ credentials.json not found! Please upload it.")
                    return False

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def send_email(self, to, subject, body):
        """Actually send an email"""
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            message = {'raw': raw}

            result = self.service.users().messages().send(
                userId='me', body=message).execute()

            return True, f"Email sent! Message ID: {result['id']}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"

    def get_recent_emails(self, max_results=10):
        """Get recent emails"""
        try:
            results = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me', id=msg['id']).execute()

                headers = msg_data['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')

                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': sender,
                    'snippet': msg_data['snippet']
                })

            return emails
        except Exception as e:
            st.error(f"Error fetching emails: {str(e)}")
            return []

# Save this as gmail_integration.py
