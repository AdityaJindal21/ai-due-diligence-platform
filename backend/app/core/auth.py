from __future__ import annotations

import os
import jwt
from datetime import datetime, timedelta

SECRET = os.environ.get("APP_SECRET", "devsecret")


def create_token(user_id: str, expires_hours: int = 24) -> str:
    payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(hours=expires_hours)}
    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=["HS256"])
*** End Patch