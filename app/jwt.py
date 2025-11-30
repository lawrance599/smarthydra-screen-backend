import jwt
from app.settings import load_settings
from datetime import datetime, timedelta, timezone
def make_jwt(username: str, expore_minutes: int = 1440) -> str:
    settings = load_settings()
    secret_key = settings.secret_key
    algorithm = settings.algorithm
    
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expore_minutes)
    payload = {
        "exp": expire,
        "iat": now,
        "sub": username,
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)
    