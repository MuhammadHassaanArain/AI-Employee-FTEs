import pickle
import os
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(__file__)
TOKEN_FILE = os.path.join(BASE_DIR, "credentials", "gmail_token.pkl")

def get_gmail_service():
    with open(TOKEN_FILE, "rb") as token:
        creds = pickle.load(token)

    return build("gmail", "v1", credentials=creds)

if __name__ == "__main__":
    service = get_gmail_service()
    results = service.users().messages().list(
        userId="me",
        maxResults=5
    ).execute()

    messages = results.get("messages", [])
    print("📬 Recent messages:")
    for m in messages:
        print("-", m["id"])