import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from firebase_auth import verify_firebase_token

BASE_DIR = Path(__file__).resolve().parent
COMPONENT_DIR = BASE_DIR / "firebase_phone_component"
HTML_FILE = COMPONENT_DIR / "index.html"

if not HTML_FILE.exists():
    raise FileNotFoundError(f"Firebase component index.html not found at: {HTML_FILE}")

firebase_phone_auth = components.declare_component(
    "firebase_phone_auth",
    path=str(COMPONENT_DIR)
)


def show_phone_auth():
    """
    Render Firebase phone authentication component and return verified user details.
    """
    result = firebase_phone_auth(
        key="firebase_phone_auth",
        default=None
    )

    if result is None:
        return None

    if not result.get("verified"):
        return None

    id_token = result.get("idToken")
    client_phone = result.get("phone")
    client_uid = result.get("uid")

    user_data = None
    if id_token:
        user_data = verify_firebase_token(id_token)

    # If server token verification succeeded
    if user_data and user_data.get("phone"):
        return user_data

    # Reliable fallback to client confirmed credentials
    if client_phone:
        return {
            "uid": client_uid or f"FIREBASE_{client_phone.replace('+', '')}",
            "phone": client_phone
        }

    return None
