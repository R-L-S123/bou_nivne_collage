import os
import json
import requests

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow


CLIENT_SECRET_FILE = "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/photospicker.mediaitems.readonly"
]


TOKEN_FILE = "token.json"


def get_authorization_url():
    """
    יוצר URL להתחברות Google OAuth
    """

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:5000/oauth/callback"
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    return authorization_url, state



def save_token(flow):
    """
    שומר את הטוקן אחרי התחברות
    """

    credentials = flow.credentials

    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())



def load_credentials():
    """
    טוען התחברות קיימת
    """

    if not os.path.exists(TOKEN_FILE):
        return None

    return Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )



def create_picker_session(credentials):
    """
    יוצר Session חדש של Google Photos Picker
    """

    url = "https://photospicker.googleapis.com/v1/sessions"

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    body = {
        "pickerConfig": {
            "mediaTypeFilter": {
                "mediaTypes": ["PHOTO"]
            }
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )

    response.raise_for_status()

    return response.json()



def get_selected_media_items(credentials, session_id):
    """
    מקבל את התמונות שהמשתמש בחר
    """

    url = (
        "https://photospicker.googleapis.com/v1/"
        f"mediaItems?sessionId={session_id}"
    )

    headers = {
        "Authorization": f"Bearer {credentials.token}"
    }

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    return response.json()



def save_photos_json(media_items):
    """
    שומר את התמונות לקובץ
    """

    os.makedirs("data", exist_ok=True)

    with open(
        "data/photos.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            media_items,
            f,
            ensure_ascii=False,
            indent=4
        )
