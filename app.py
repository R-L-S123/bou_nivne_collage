from flask import Flask, render_template, redirect, request, session, url_for
import os
from google_photos import download_media_items
from google_auth_oauthlib.flow import Flow
import requests

from google_photos import (
    get_authorization_url,
    save_token,
    load_credentials,
    create_picker_session,
    get_selected_media_items,
    save_photos_json,
    CLIENT_SECRET_FILE,
    SCOPES
)


app = Flask(__name__)

app.secret_key = "change-this-secret-key"


# בשביל פיתוח מקומי בלבד
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/login")
def login():

    authorization_url, state = get_authorization_url()

    session["state"] = state

    return redirect(authorization_url)



@app.route("/oauth/callback")
def oauth_callback():

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        state=session["state"],
        redirect_uri="https://bou-nivne-collage.onrender.com/oauth/callback"
    )


    flow.fetch_token(
        authorization_response=request.url
    )


    save_token(flow)


    return redirect("/picker")



@app.route("/picker")
def picker():

    credentials = load_credentials()

    if credentials is None:
        return redirect("/login")


    session_data = create_picker_session(
        credentials
    )


    session["picker_session_id"] = (
        session_data["id"]
    )


    picker_uri = (
        session_data["pickerUri"]
    )


    return render_template(
        "picker.html",
        picker_uri=picker_uri,
        session_id=session_data["id"]
    )

@app.route("/picker/complete")
def picker_complete():

    credentials = load_credentials()

    session_id = session.get(
        "picker_session_id"
    )


    if not session_id:
        return "No picker session"



    photos = get_selected_media_items(
        credentials,
        session_id
    )


    save_photos_json(
        photos
    )


    image_paths = download_media_items(
        credentials,
        photos
    )

    from collage_generator import create_grid
    grid_path = create_grid(
        image_paths
    )
    session["grid_path"] = grid_path
    
    from collage_generator import save_heart_mask
    from collage_generator import save_heart_overlay
    overlay_path = save_heart_overlay()
    session["overlay_path"] = overlay_path
    
    from collage_generator import create_collage
    session["image_paths"] = image_paths
    
    return redirect(
        "/editor"
    )

@app.route("/gallery")
def gallery():

    return render_template(
        "gallery.html"
    )

@app.route("/picker/status")
def picker_status():

    credentials = load_credentials()

    session_id = session.get(
        "picker_session_id"
    )


    url = (
        f"https://photospicker.googleapis.com/v1/sessions/{session_id}"
    )


    headers = {
        "Authorization":
        f"Bearer {credentials.token}"
    }


    response = requests.get(
        url,
        headers=headers
    )


    data = response.json()


    return {
        "done":
        data.get(
            "mediaItemsSet",
            False
        )
    }

@app.route("/editor")
def editor():

    return render_template(
        "editor.html",
        grid_path=session.get("grid_path"),
        overlay_path=session.get("overlay_path")
    )

@app.route("/create_collage", methods=["POST"])
def create_collage_route():

    data = request.get_json()

    x = data["x"]
    y = data["y"]

    session["grid_x"] = x
    session["grid_y"] = y

    return {
        "status": "ok"
    }

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
