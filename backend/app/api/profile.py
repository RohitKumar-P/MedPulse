import json
import os
import uuid
from datetime import datetime, timezone

from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.db import SessionLocal
from app.api.auth import get_current_user


router = APIRouter(
    prefix="/profile",
    tags=["Health Profile"],
)


def utcnow():
    return datetime.now(timezone.utc)


def get_cipher():
    key = os.getenv("AEGIS_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("AEGIS_ENCRYPTION_KEY is not configured")
    return Fernet(key.encode())


def ensure_table():
    db = SessionLocal()
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS health_profiles (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL UNIQUE
                    REFERENCES users(id) ON DELETE CASCADE,
                encrypted_profile TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
        """))
        db.commit()
    finally:
        db.close()


ensure_table()


class HealthProfile(BaseModel):
    name: str = Field(default="", max_length=120)
    date_of_birth: str = Field(default="", max_length=20)
    age: int | None = Field(default=None, ge=1, le=120)
    gender: str = Field(default="", max_length=40)

    height_cm: float | None = Field(default=None, gt=30, lt=250)
    weight_kg: float | None = Field(default=None, gt=1, lt=500)
    bmi: float | None = None

    blood_pressure: str = Field(default="", max_length=30)
    resting_heart_rate: float | None = Field(default=None, ge=20, le=250)
    spo2: float | None = Field(default=None, ge=50, le=100)

    activity_level: str = Field(default="", max_length=50)
    exercise_frequency: str = Field(default="", max_length=80)
    smoking: str = Field(default="", max_length=50)
    alcohol: str = Field(default="", max_length=50)
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    sleep_quality: str = Field(default="", max_length=50)
    water_intake_liters: float | None = Field(default=None, ge=0, le=20)

    existing_conditions: str = Field(default="", max_length=3000)
    medications: str = Field(default="", max_length=3000)
    allergies: str = Field(default="", max_length=3000)
    family_history: str = Field(default="", max_length=3000)

    goals: list[str] = Field(default_factory=list)


def decrypt_profile(value: str):
    try:
        return json.loads(
            get_cipher().decrypt(
                value.encode()
            ).decode()
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt health profile",
        )


def encrypt_profile(value: dict):
    return get_cipher().encrypt(
        json.dumps(
            value,
            separators=(",", ":"),
        ).encode()
    ).decode()


@router.get("/me")
def get_profile(
    current_user=Depends(get_current_user),
):
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT encrypted_profile, completed
                FROM health_profiles
                WHERE user_id = :user_id
            """),
            {"user_id": current_user.id},
        ).mappings().first()

        if not row:
            return {
                "completed": False,
                "profile": None,
            }

        return {
            "completed": bool(row["completed"]),
            "profile": decrypt_profile(
                row["encrypted_profile"]
            ),
        }

    finally:
        db.close()


@router.put("/me")
def save_profile(
    data: HealthProfile,
    current_user=Depends(get_current_user),
):
    profile = data.model_dump()

    if (
        profile["height_cm"] is not None
        and profile["weight_kg"] is not None
    ):
        height_m = profile["height_cm"] / 100
        profile["bmi"] = round(
            profile["weight_kg"] / (height_m * height_m),
            1,
        )

    profile["username"] = current_user.username

    encrypted = encrypt_profile(profile)
    now = utcnow()

    db = SessionLocal()

    try:
        existing = db.execute(
            text("""
                SELECT id
                FROM health_profiles
                WHERE user_id = :user_id
            """),
            {"user_id": current_user.id},
        ).scalar()

        if existing:
            db.execute(
                text("""
                    UPDATE health_profiles
                    SET encrypted_profile = :profile,
                        completed = TRUE,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                """),
                {
                    "profile": encrypted,
                    "updated_at": now,
                    "user_id": current_user.id,
                },
            )
        else:
            db.execute(
                text("""
                    INSERT INTO health_profiles
                    (
                        id,
                        user_id,
                        encrypted_profile,
                        completed,
                        created_at,
                        updated_at
                    )
                    VALUES
                    (
                        :id,
                        :user_id,
                        :profile,
                        TRUE,
                        :created_at,
                        :updated_at
                    )
                """),
                {
                    "id": str(uuid.uuid4()),
                    "user_id": current_user.id,
                    "profile": encrypted,
                    "created_at": now,
                    "updated_at": now,
                },
            )

        db.commit()

        return {
            "status": "success",
            "completed": True,
            "profile": profile,
        }

    finally:
        db.close()
