import os
import base64
import json
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly']

class GmailIntegrationStreamlit:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate using Streamlit secrets"""
        creds = None

        # Check if we have credentials in Streamlit secrets
        if 'GMAIL_CREDENTIALS' in st.secrets:
            try:
                # Create credentials from Streamlit secrets
                credentials_data = st.secrets['GMAIL_CREDENTIALS']
                
                # Create a temporary credentials file
                with open('temp_credentials.json', 'w') as f:
                    json.dump(credentials_data, f)
                
                # Use the credentials file for authentication
                flow = InstalledAppFlow.from_client_secrets_file(
                    'temp_credentials.json', SCOPES)
                
                # For Streamlit Cloud, we need to handle OAuth differently
                # This will redirect to Google OAuth
                creds = flow.run_local_server(port=8080, host='localhost')
                
                # Clean up temp file
                os.remove('temp_credentials.json')
                
            except Exception as e:
                st.error(f"Gmail authentication error: {e}")
                return False
        else:
            st.warning("Gmail credentials not found in Streamlit secrets. Please add GMAIL_CREDENTIALS to your secrets.")
            return False

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            st.success("✅ Gmail integration authenticated successfully!")
            return True
        except Exception as e:
            st.error(f"Error building Gmail service: {e}")
            return False

    def send_email(self, to, subject, body):
        """Send an email via Gmail API"""
        try:
            if not self.service:
                return False, "Gmail service not initialized"

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
        """Get recent emails from Gmail"""
        try:
            if not self.service:
                return []

            results = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me', id=msg['id']).execute()

                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

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

    def create_mock_service(self):
        """Create a mock Gmail service for demo purposes"""
        class MockGmailService:
            def users(self):
                return MockUsers()
        return MockGmailService()

class MockUsers:
    def messages(self):
        return MockMessages()

class MockMessages:
    def list(self, **kwargs):
        return MockListResponse()
    
    def get(self, **kwargs):
        return MockGetResponse()
    
    def send(self, **kwargs):
        return MockSendResponse()

class MockListResponse:
    def execute(self):
        return {
            'messages': [
                {'id': 'mock_id_1'},
                {'id': 'mock_id_2'}
            ]
        }

class MockGetResponse:
    def execute(self):
        return {
            'id': 'mock_id',
            'snippet': 'This is a mock email snippet',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Mock Email Subject'},
                    {'name': 'From', 'value': 'mock@example.com'}
                ]
            }
        }

class MockSendResponse:
    def execute(self):
        return {'id': 'mock_message_id'}

# Usage example
if __name__ == "__main__":
    gmail = GmailIntegrationStreamlit()
    if gmail.service:
        print("Gmail integration ready!")
    else:
        print("Gmail integration failed!") 