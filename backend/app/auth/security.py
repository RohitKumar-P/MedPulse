import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jose import jwt
import bcrypt

load_dotenv(
    Path(__file__).resolve().parent.parent.parent / ".env"
)

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

# Short-lived access session.
JWT_EXPIRE_MINUTES = 10

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET is not configured"
    )


def hash_password(password):

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password must be 72 UTF-8 bytes or shorter"
        )

    return bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    password,
    password_hash
):

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    return bcrypt.checkpw(
        password_bytes,
        password_hash.encode("utf-8")
    )


def create_access_token(
    subject,
    role
):

    now = datetime.now(timezone.utc)

    expires = (
        now
        + timedelta(
            minutes=JWT_EXPIRE_MINUTES
        )
    )

    # Cryptographically random session/token ID.
    jti = secrets.token_urlsafe(32)

    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": expires,
        "jti": jti,
        "type": "access"
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token):

    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM]
    )

    if payload.get("type") != "access":
        raise ValueError(
            "Invalid token type"
        )

    if not payload.get("jti"):
        raise ValueError(
            "Missing session identifier"
        )

    return payload
