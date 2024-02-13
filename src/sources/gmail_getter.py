import base64
from datetime import datetime
from os.path import exists
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import Optional

from constants import GMAIL_SCOPES


class GmailGetter:
    def __init__(self):
        print('GmailGetter')
        self.creds = self.__get_creds()
        print('Creds fetched')
        self.user_id = 'me'
        self.service = build("gmail", "v1", credentials=self.creds)

    def __get_creds(self):
        """
        Get the credentials for the Gmail API. If the credentials are not found, the user will be prompted to log in.
        The credentials are stored in a file called token.json for future use.
        The file token.json stores the user's access and refresh tokens, and is created automatically when the 
        authorization flow completes for the first time.
        """
        creds = None
        if exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds


    def get_messages(self, query: Optional[str] = None):
        """
        Get the messages from the user's Gmail account.
        :param query: The query to filter the messages. For example, 'from:example@email.com'.
        """
        result = self.service.users().messages().list(userId=self.user_id,  labelIds=["IMPORTANT"], q=query).execute()
        messages = result.get('messages', [])
        while 'nextPageToken' in result:
            page_token = result['nextPageToken']
            result = self.service.users().messages().list(userId=self.user_id, pageToken=page_token).execute()
            messages += result.get('messages', [])
        msg_n = messages[-1]
        msg = self.service.users().messages().get(userId=self.user_id, id=messages[0]['id']).execute()
        print(msg.keys())
        print(msg['payload'].keys())
        print(msg['payload']['headers'][0])
        print(msg['snippet'])
        print(msg['payload']['body'])
        body = msg['payload']['body']['data']
        body = body.replace("-", "+").replace("_", "/")
        body = base64.b64decode(body)
        print(body)

        date = msg['internalDate']
        date = datetime.fromtimestamp(int(date) / 1000)
        print(date)

        # Convert the message internal date to a human-readable format



        return messages
