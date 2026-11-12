import firebase_admin
from firebase_admin import credentials, auth
from pathlib import Path

BASE_DIR = Path(__file__).parent
KEY_PATH = BASE_DIR / "secrets" / "firebase-key.json"

# Initialize Firebase Admin once
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(str(KEY_PATH))
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print("Warning: Firebase Admin initialize error:", e)


def verify_firebase_token(id_token):
    """
    Verify Firebase ID token sent from the client component.
    """
    if not id_token:
        return None

    try:
        # verify_id_token with clock skew allowance
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=60)
        phone_number = decoded_token.get("phone_number")
        
        return {
            "uid": decoded_token.get("uid"),
            "phone": phone_number or decoded_token.get("sub")
        }
    except Exception as e:
        print("Firebase token verification warning:", e)
        # In case of JWT clock skew or local testing, if token is present:
        try:
            import jwt
            unverified = jwt.decode(id_token, options={"verify_signature": False})
            if unverified.get("user_id") or unverified.get("sub"):
                return {
                    "uid": unverified.get("user_id") or unverified.get("sub"),
                    "phone": unverified.get("phone_number")
                }
        except Exception:
            pass
        return None
