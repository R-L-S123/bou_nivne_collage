from flask import Flask, render_template, redirect, session, request
import json
from flask import send_file
import io
import requests
import time

from collage import create_collage
from main import create_auth_flow, import_photos, finish_authentication


app = Flask(__name__)
app.secret_key = "change-this-secret-key"

@app.route("/finish_import")
def finish_import():

   if not wait_for_selection(creds, session_id):
    return {"done": False}

    data = get_selected_photos(creds, session_id)
    
    photos = save_photos_to_json(data, creds)
    
    create_collage()
    
    return {"done": True}


@app.route("/photo/<int:index>")
def get_photo(index):

    with open(
        "photos.json",
        encoding="utf-8"
    ) as f:
        photos = json.load(f)


    photo = photos[index]


    response = requests.get(
        photo["url"] + "=w1000-h1000",
        headers={
            "Authorization":
            f"Bearer {photo['token']}"
        }
    )


    return send_file(
        io.BytesIO(response.content),
        mimetype="image/jpeg"
    )



@app.route("/")
def home():

    try:

        with open(
            "photos.json",
            "r",
            encoding="utf-8"
        ) as f:

            photos = json.load(f)


    except:

        photos = []


    for photo in photos:

        photo["display_url"] = (
            photo["url"] +
            "=w500-h500"
        )


    return render_template(
        "gallery.html",
        photos=photos,
        collage_version=time.time()
    )



@app.route("/import")
def import_google_photos():

    flow = create_auth_flow()


    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )


    session["code_verifier"] = flow.code_verifier


    return redirect(authorization_url)



@app.route("/oauth/callback")
def oauth_callback():


    creds = finish_authentication(
        session["code_verifier"],
        request.url
    )

    picker_session = import_photos(
        creds
    )
    
    
    session["picker_id"] = picker_session["id"]
    session["access_token"] = creds.token
    
    
    return redirect(
        picker_session["pickerUri"]
    )

@app.route("/picker/complete")
def picker_complete():

    from main import (
        get_selected_photos,
        save_photos_to_json
    )


    session_id = session["picker_id"]

    token = session["access_token"]


    class TempCreds:
        def __init__(self, token):
            self.token = token


    creds = TempCreds(token)


    data = get_selected_photos(
        creds,
        session_id
    )


    photos = save_photos_to_json(
        data,
        creds
    )


    if len(photos) < 25:
        return "צריך לפחות 25 תמונות"


    create_collage()


    return redirect("/")

@app.route("/download")
def download():

    return send_file(
        "static/heart_collage.png",
        as_attachment=True,
        download_name="heart_collage.png"
    )



if __name__ == "__main__":

    app.run(
        debug=True
    )
