import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required for the personal agent
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

class GoogleWorkspaceAdapter:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.creds = None
        
    def authenticate(self):
        # Initial local OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
        self.creds = flow.run_local_server(port=0)
        
    def get_calendar_events(self, limit=10):
        service = build('calendar', 'v3', credentials=self.creds)
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=limit, singleEvents=True,
                                              orderBy='startTime').execute()
        return events_result.get('items', [])

    def get_unread_emails(self, limit=5):
        service = build('gmail', 'v1', credentials=self.creds)
        # To be implemented
        pass
