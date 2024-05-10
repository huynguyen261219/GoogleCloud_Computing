import os
import google.oauth2
import google.oauth2.credentials
import requests
from typing import Union

from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests
from google.oauth2.credentials import Credentials

from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi import HTTPException, FastAPI

from starlette.middleware.sessions import SessionMiddleware


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = (
    "449665421353-vdsk1n3bg4cnainmjnsph95jesjc20n1.apps.googleusercontent.com"
)
flow = InstalledAppFlow.from_client_secrets_file(
    client_secrets_file="client_secret.json",
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://127.0.0.1:8000/callback",
)


app = FastAPI(title="Google Login App")
app.add_middleware(SessionMiddleware, secret_key="83928382-2912912cndcdckm")


def credentials_to_dict(credentials: Credentials) -> dict:
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/login")
def login(req: Request):
    # generate authorization URL
    authorization_url, state = flow.authorization_url()

    # cache its state
    req.session["state"] = state

    return authorization_url


@app.get("/callback")
def callback(req: Request):
    try:
        # complete auth flow and get access token
        flow.fetch_token(authorization_response=str(req.url))

        # check cached state and request state is matched, if No -> abort 500
        # protect web from "XSS attack"
        if req.session["state"] != req.query_params["state"]:
            raise HTTPException(status_code=500, detail="State does not match")

        # get credentials from Oauth2
        credentials = flow.credentials
        request_session = requests.session()
        token_request = google.auth.transport.requests.Request(session=request_session)

        # verify id token from credentials after authentication flow
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID,
        )

        req.session["credentials"] = credentials_to_dict(credentials)
        req.session["google_id"] = id_info.get("sub")
        req.session["name"] = id_info.get("name")

        return RedirectResponse(url="/protected_area", status_code=301)
    except Exception as e:
        req.session.clear()
        raise e


@app.get("/protected_area")
def protected_area(req: Request):
    return f"Hello {req.session.get('name')}"


@app.post("/logout")
def logout(req: Request):
    credentials = google.oauth2.credentials.Credentials(
        **req.session.get("credentials")
    )

    # call revoke token
    revoke = requests.post(
        url="https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    status_code = getattr(revoke, "status_code")

    if status_code == 200:
        del req.session["credentials"]
        return "Credentials revoke successfully!!"

    return HTTPException(status_code=500, detail="An error occurred")
