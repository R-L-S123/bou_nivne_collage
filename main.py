import requests
import time
import os
import json
import webbrowser

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/photospicker.mediaitems.readonly"
]


def authenticate():

    creds = None

    try:
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )
    except:
        pass


    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:

            credentials_data = json.loads(
            os.environ["GOOGLE_CREDENTIALS"])
                
            flow = InstalledAppFlow.from_client_config(
                credentials_data,
                SCOPES)
              
            creds = flow.run_local_server(
                port=0)


        with open("token.json", "w") as f:
            f.write(creds.to_json())


    return creds



def create_picker_session(creds):

    response = requests.post(
        "https://photospicker.googleapis.com/v1/sessions",

        headers={
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        },

        json={}
    )


    response.raise_for_status()

    return response.json()



def wait_for_selection(creds, session_id):

    while True:

        response = requests.get(

            f"https://photospicker.googleapis.com/v1/sessions/{session_id}",

            headers={
                "Authorization": f"Bearer {creds.token}"
            }
        )


        response.raise_for_status()

        data = response.json()


        if data.get("mediaItemsSet"):
            break


        time.sleep(2)



def get_selected_photos(creds, session_id):

    response = requests.get(

        "https://photospicker.googleapis.com/v1/mediaItems",

        headers={
            "Authorization": f"Bearer {creds.token}"
        },

        params={
            "sessionId": session_id
        }
    )


    response.raise_for_status()

    return response.json()



def save_photos_to_json(data, creds):

    photos = []


    for photo in data.get("mediaItems", []):

        media_file = photo.get("mediaFile", {})


        photos.append({

            "id": photo.get("id"),

            "date": photo.get("createTime"),

            "url": media_file.get("baseUrl"),

            "token": creds.token,

            "type": media_file.get("mimeType"),

            "people": []

        })


    with open(
        "photos.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            photos,
            f,
            ensure_ascii=False,
            indent=4
        )


    return photos


def import_photos():

    creds = authenticate()


    session = create_picker_session(
        creds
    )


    picker_url = session["pickerUri"]

    print("\nפותח את Google Photos Picker...")

    webbrowser.open(picker_url)


    session_id = session["id"]


    wait_for_selection(
        creds,
        session_id
    )


    data = get_selected_photos(
        creds,
        session_id
    )


    photos = save_photos_to_json(
        data, creds
    )


    return photos



if __name__ == "__main__":


    photos = import_photos()


    print("\nנבחרו תמונות:")

    for photo in photos:

        print(
            photo["id"],
            photo["date"]
        )


    print(
        f"\nנשמרו {len(photos)} תמונות"
    )
