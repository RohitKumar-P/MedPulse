import os
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Cookie,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from fastapi.responses import JSONResponse

from pydantic import BaseModel

from app.db import SessionLocal
from app.models import User

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    JWT_EXPIRE_MINUTES,
)

from app.auth.session_store import (
    create_refresh_session,
    get_refresh_session_user,
    rotate_refresh_session,
    revoke_refresh_session,
    revoke_all_user_sessions,
)

from app.auth.rate_limit import (
    allow_request,
    LOGIN_LIMIT,
    REGISTER_LIMIT,
)


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

bearer = HTTPBearer()


REFRESH_COOKIE = "medpulse_refresh"

REFRESH_MAX_AGE = (
    7 * 24 * 60 * 60
)    
REFRESH_COOKIE_SECURE = (
    os.getenv("MEDPULSE_COOKIE_SECURE", "false").lower() == "true"
)


class RegisterRequest(BaseModel):

    username: str
    password: str


class LoginRequest(BaseModel):

    username: str
    password: str


@router.post("/register")
def register(
    data: RegisterRequest
):

    username = data.username.strip()

    if not username:

        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    if len(username) > 120:

        raise HTTPException(
            status_code=400,
            detail="Username is too long"
        )

    if len(data.password) < 12:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must contain "
                "at least 12 characters"
            )
        )

    if not allow_request(
        f"register:{username.lower()}",
        REGISTER_LIMIT
    ):

        raise HTTPException(
            status_code=429,
            detail=(
                "Too many registration "
                "attempts. Try again later."
            )
        )

    db = SessionLocal()

    try:

        existing = (
            db.query(User)
            .filter(
                User.username
                == username
            )
            .first()
        )

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            )

        # Public registration can ONLY
        # create patient accounts.
        user = User(
            username=username,
            password_hash=hash_password(
                data.password
            ),
            role="patient",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        }

    finally:

        db.close()


@router.post("/login")
def login(
    data: LoginRequest
):

    username = data.username.strip()

    if not allow_request(
        f"login:{username.lower()}",
        LOGIN_LIMIT
    ):

        raise HTTPException(
            status_code=429,
            detail=(
                "Too many login attempts. "
                "Try again later."
            )
        )

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.username
                == username
            )
            .first()
        )

        if (
            not user
            or not user.is_active
            or not verify_password(
                data.password,
                user.password_hash
            )
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        access_token = create_access_token(
            user.id,
            user.role
        )

        refresh_token = (
            create_refresh_session(
                user.id
            )
        )

        response = JSONResponse({
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in_minutes":
                JWT_EXPIRE_MINUTES,
            "user": {
                "id": user.id,
                "username":
                    user.username,
                "role":
                    user.role,
            },
        })

        response.set_cookie(
            key=REFRESH_COOKIE,
            value=refresh_token,
            httponly=True,
            secure=REFRESH_COOKIE_SECURE,
            samesite="strict",
            max_age=REFRESH_MAX_AGE,
            path="/auth",
        )

        return response

    finally:

        db.close()


@router.post("/refresh")
def refresh_access_token(
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_COOKIE
    )
):

    if not refresh_token:

        raise HTTPException(
            status_code=401,
            detail="Refresh session required"
        )

    user_id = (
        get_refresh_session_user(
            refresh_token
        )
    )

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh session"
        )

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if (
            not user
            or not user.is_active
        ):

            raise HTTPException(
                status_code=401,
                detail="User unavailable"
            )

        new_refresh_token = (
            rotate_refresh_session(
                refresh_token,
                user.id
            )
        )

        if not new_refresh_token:

            raise HTTPException(
                status_code=401,
                detail=(
                    "Refresh session expired "
                    "or revoked"
                )
            )

        new_access_token = (
            create_access_token(
                user.id,
                user.role
            )
        )

        response = JSONResponse({
            "access_token":
                new_access_token,
            "token_type":
                "bearer",
            "expires_in_minutes":
                JWT_EXPIRE_MINUTES,
        })

        response.set_cookie(
            key=REFRESH_COOKIE,
            value=new_refresh_token,
            httponly=True,
            secure=REFRESH_COOKIE_SECURE,
            samesite="strict",
            max_age=REFRESH_MAX_AGE,
            path="/auth",
        )

        return response

    finally:

        db.close()


@router.post("/logout")
def logout(
    refresh_token: str | None = Cookie(
        default=None,
        alias=REFRESH_COOKIE
    )
):

    if refresh_token:

        revoke_refresh_session(
            refresh_token
        )

    response = JSONResponse({
        "status": "success",
        "message": "Session ended"
    })

    response.delete_cookie(
        key=REFRESH_COOKIE,
        path="/auth"
    )

    return response


@router.post("/logout-all")
def logout_all(
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):

    current_user = get_current_user(
        credentials
    )

    revoke_all_user_sessions(
        current_user.id
    )

    return {
        "status": "success",
        "message": (
            "All refresh sessions revoked"
        )
    }


def get_current_user(
    credentials:
        HTTPAuthorizationCredentials
        = Depends(bearer),
):

    try:

        payload = decode_access_token(
            credentials.credentials
        )

        user_id = payload.get(
            "sub"
        )

        role = payload.get(
            "role"
        )

        jti = payload.get(
            "jti"
        )

        if not user_id:
            raise ValueError()

        if not role:
            raise ValueError()

        if not jti:
            raise ValueError()

    except Exception:

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid or expired "
                "session"
            )
        )

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if (
            not user
            or not user.is_active
        ):

            raise HTTPException(
                status_code=401,
                detail=(
                    "User is inactive "
                    "or unavailable"
                )
            )

        return user

    finally:

        db.close()


def require_roles(*roles):

    def dependency(
        user=Depends(
            get_current_user
        ),
    ):

        if user.role not in roles:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Insufficient "
                    "permissions"
                )
            )

        return user

    return dependency

