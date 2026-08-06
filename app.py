from flask import Flask, render_template, redirect
import json
from flask import send_file
import io
import requests
import time

from collage import create_collage
from main import create_auth_flow


app = Flask(__name__)


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

    return redirect(authorization_url)

@app.route("/oauth/callback")
def oauth_callback():

    from main import finish_authentication

    creds = finish_authentication()

    with open("token.json", "w") as f:
        f.write(creds.to_json())


    photos = import_photos()

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
