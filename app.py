from flask import Flask, render_template, redirect, request, session, url_for
import os

from google_auth_oauthlib.flow import Flow

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
        redirect_uri="http://localhost:5000/oauth/callback"
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
        picker_uri=picker_uri
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


    return redirect("/gallery")



@app.route("/gallery")
def gallery():

    return render_template(
        "gallery.html"
    )



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
