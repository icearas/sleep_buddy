import streamlit as st
from authlib.integrations.requests_client import OAuth2Session


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
SCOPES = "openid email profile"


def get_redirect_uri() -> str:
    # Works both locally and on Streamlit Cloud
    try:
        base = st.secrets.get("APP_URL", "http://localhost:8501")
    except Exception:
        base = "http://localhost:8501"
    return f"{base}/callback"


def get_oauth_session() -> OAuth2Session:
    return OAuth2Session(
        client_id=st.secrets["GOOGLE_CLIENT_ID"],
        client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
        scope=SCOPES,
        redirect_uri=get_redirect_uri(),
    )


def get_login_url() -> str:
    oauth = get_oauth_session()
    url, state = oauth.create_authorization_url(GOOGLE_AUTH_URL)
    st.session_state["oauth_state"] = state
    return url


def handle_callback(code: str) -> dict | None:
    """
    Exchange authorization code for user info.
    Returns dict with 'email' and 'name', or None on failure.
    """
    try:
        oauth = get_oauth_session()
        token = oauth.fetch_token(
            GOOGLE_TOKEN_URL,
            code=code,
            grant_type="authorization_code",
        )
        resp = oauth.get(GOOGLE_USERINFO_URL)
        user_info = resp.json()
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name", ""),
        }
    except Exception as e:
        st.error(f"OAuth error: {e}")
        return None


def is_logged_in() -> bool:
    return "user_email" in st.session_state and bool(st.session_state["user_email"])


def logout():
    for key in ["user_email", "user_name", "oauth_state"]:
        st.session_state.pop(key, None)
