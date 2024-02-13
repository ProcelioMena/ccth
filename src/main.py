from sources.gmail_getter import GmailGetter
import datetime

from googleapiclient.errors import HttpError



def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        print("token.json exists")
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        print('after token')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print("creds is not valid")
        if creds and creds.expired and creds.refresh_token:
            print("creds is expired")
            creds.refresh(Request())
    else:
        print("creds is valid")
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        print('creds:', creds)
    # Save the credentials for the next run
    print('before saving')
    with open("token.json", "w") as token:
        token.write(creds.to_json())

  # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    # fetch emails on INBOX by date
    result = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="after:2024/01/02")
        .execute()
    )
    print(result.keys())
    print(len(result["messages"]))
    # loop through the emails using the nextPageToken
    if "nextPageToken" in result:
        while "nextPageToken" in result:
            page_token = result["nextPageToken"]
            result = (
                service.users()
                .messages()
                .list(userId="me", pageToken=page_token)
                .execute()
            )
            # print the email snippet for each email
            for message in result["messages"]:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"])
                    .execute()
                )
                print(msg["snippet"])
                # print date from each email
                msg["internalDate"]
                # convert the date to a readable format
                print(
                    datetime.datetime.fromtimestamp(int(msg["internalDate"]) / 1000)
                )


def get_messages(service, user_id="me"):
    try:
        response = service.users().messages().list(userId=user_id).execute()
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId=user_id, pageToken=page_token)
                .execute()
            )
            messages.extend(response["messages"])

        return messages
    except:
        print('An error occurred')





if __name__ == "__main__":
    messages = GmailGetter().get_messages(query='after:2024/01/01')
    print(len(messages))
