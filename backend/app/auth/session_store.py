import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    insert,
    select,
    update,
)

from app.db import engine


metadata = MetaData()


refresh_sessions = Table(
    "refresh_sessions",

    metadata,

    Column(
        "id",
        String(64),
        primary_key=True
    ),

    Column(
        "user_id",
        String(36),
        nullable=False,
        index=True
    ),

    Column(
        "token_hash",
        String(128),
        nullable=False,
        unique=True,
        index=True
    ),

    Column(
        "expires_at",
        DateTime(timezone=True),
        nullable=False
    ),

    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False
    ),

    Column(
        "revoked",
        Boolean,
        nullable=False,
        default=False
    ),

    Column(
        "replaced_by",
        String(64),
        nullable=True
    ),
)


metadata.create_all(engine)


REFRESH_DAYS = 7


def _hash_token(token):

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_refresh_session(user_id):

    raw_token = secrets.token_urlsafe(64)

    session_id = secrets.token_urlsafe(32)

    now = datetime.now(timezone.utc)

    expires = (
        now
        + timedelta(days=REFRESH_DAYS)
    )

    with engine.begin() as conn:

        conn.execute(
            insert(refresh_sessions).values(
                id=session_id,
                user_id=str(user_id),
                token_hash=_hash_token(
                    raw_token
                ),
                expires_at=expires,
                created_at=now,
                revoked=False,
                replaced_by=None,
            )
        )

    return raw_token


def get_refresh_session_user(
    raw_token
):

    token_hash = _hash_token(
        raw_token
    )

    now = datetime.now(timezone.utc)

    with engine.connect() as conn:

        row = conn.execute(
            select(
                refresh_sessions.c.user_id,
                refresh_sessions.c.revoked,
                refresh_sessions.c.expires_at,
            )
            .where(
                refresh_sessions.c.token_hash
                == token_hash
            )
        ).mappings().first()

    if not row:
        return None

    if row["revoked"]:
        return None

    if row["expires_at"] <= now:
        return None

    return row["user_id"]


def rotate_refresh_session(
    raw_token,
    user_id
):

    token_hash = _hash_token(
        raw_token
    )

    now = datetime.now(timezone.utc)

    with engine.begin() as conn:

        row = conn.execute(
            select(refresh_sessions)
            .where(
                refresh_sessions.c.token_hash
                == token_hash
            )
        ).mappings().first()

        if not row:
            return None

        if row["revoked"]:
            return None

        if row["expires_at"] <= now:
            return None

        if str(row["user_id"]) != str(user_id):
            return None

        new_token = secrets.token_urlsafe(64)

        new_id = secrets.token_urlsafe(32)

        new_expires = (
            now
            + timedelta(days=REFRESH_DAYS)
        )

        conn.execute(
            update(refresh_sessions)
            .where(
                refresh_sessions.c.id
                == row["id"]
            )
            .values(
                revoked=True,
                replaced_by=new_id
            )
        )

        conn.execute(
            insert(refresh_sessions).values(
                id=new_id,
                user_id=str(user_id),
                token_hash=_hash_token(
                    new_token
                ),
                expires_at=new_expires,
                created_at=now,
                revoked=False,
                replaced_by=None,
            )
        )

    return new_token


def revoke_refresh_session(
    raw_token
):

    token_hash = _hash_token(
        raw_token
    )

    with engine.begin() as conn:

        conn.execute(
            update(refresh_sessions)
            .where(
                refresh_sessions.c.token_hash
                == token_hash
            )
            .values(
                revoked=True
            )
        )


def revoke_all_user_sessions(
    user_id
):

    with engine.begin() as conn:

        conn.execute(
            update(refresh_sessions)
            .where(
                refresh_sessions.c.user_id
                == str(user_id)
            )
            .where(
                refresh_sessions.c.revoked
                == False
            )
            .values(
                revoked=True
            )
        )
