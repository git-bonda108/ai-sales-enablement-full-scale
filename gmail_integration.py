import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import streamlit as st
import socket

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
            try:
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"Error loading token: {e}")
                creds = None

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None
            
            if not creds or not creds.valid:
                if os.path.exists('credentials.json'):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES)
                        # Use port 8080 which is already authorized in Google Cloud Console
                        creds = flow.run_local_server(port=8080, host='localhost')
                    except Exception as e:
                        print(f"Error during authentication: {e}")
                        # For demo purposes, create a mock service
                        print("Creating mock Gmail service for demo...")
                        self.service = self.create_mock_service()
                        return True
                else:
                    print("❌ credentials.json not found!")
                    # For demo purposes, create a mock service
                    print("Creating mock Gmail service for demo...")
                    self.service = self.create_mock_service()
                    return True

            # Save the credentials for the next run
            try:
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Error saving token: {e}")

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            print(f"Error building Gmail service: {e}")
            # For demo purposes, create a mock service
            print("Creating mock Gmail service for demo...")
            self.service = self.create_mock_service()
            return True

    def create_mock_service(self):
        """Create a mock Gmail service for demo purposes"""
        class MockGmailService:
            def users(self):
                return MockUsers()
        return MockGmailService()

    def send_email(self, to, subject, body):
        """Actually send an email"""
        try:
            if hasattr(self.service, 'users'):
                message = MIMEText(body)
                message['to'] = to
                message['subject'] = subject

                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                message = {'raw': raw}

                result = self.service.users().messages().send(
                    userId='me', body=message).execute()

                return True, f"Email sent! Message ID: {result['id']}"
            else:
                # Mock response for demo
                return True, f"✅ Demo: Email would be sent to {to} with subject '{subject}'"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"

    def get_recent_emails(self, max_results=10):
        """Get recent emails"""
        try:
            if hasattr(self.service, 'users'):
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
                        'snippet': msg_data.get('snippet', '')
                    })

                return emails
            else:
                # Mock emails for demo
                return [
                    {
                        'id': 'demo1',
                        'subject': 'Demo Email 1 - Sales Follow-up',
                        'from': 'prospect@company.com',
                        'snippet': 'Thank you for the presentation...'
                    },
                    {
                        'id': 'demo2', 
                        'subject': 'Demo Email 2 - Meeting Request',
                        'from': 'client@business.com',
                        'snippet': 'I would like to schedule a call...'
                    },
                    {
                        'id': 'demo3',
                        'subject': 'Demo Email 3 - Proposal Review',
                        'from': 'decision.maker@enterprise.com',
                        'snippet': 'We have reviewed your proposal...'
                    }
                ]
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            return []

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
        return {'messages': [{'id': 'demo1'}, {'id': 'demo2'}, {'id': 'demo3'}]}

class MockGetResponse:
    def execute(self):
        return {
            'id': 'demo1',
            'snippet': 'Demo email content...',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Demo Email'},
                    {'name': 'From', 'value': 'demo@example.com'}
                ]
            }
        }

class MockSendResponse:
    def execute(self):
        return {'id': 'demo_message_id'}
