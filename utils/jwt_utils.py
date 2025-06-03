from datetime import datetime, timedelta
import jwt
from config import Config
import json

def generate_token(data, expires_in=128):
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=expires_in),
        "iat": datetime.utcnow(),
        "sub": json.dumps(data)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return json.loads(payload["sub"])
    except jwt.ExpiredSignatureError:
        print("❌ Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        print("❌ Token inválido:", e)
        return None

