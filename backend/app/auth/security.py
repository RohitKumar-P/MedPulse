from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import uuid

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
)

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not configured")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password, password_hash)
    except Exception:
        return False

def create_access_token(subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expires,
        "type": "access",
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("type") != "access":
            return None

        return payload

    except JWTError:
        return None
