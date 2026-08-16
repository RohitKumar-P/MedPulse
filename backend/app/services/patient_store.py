from datetime import datetime, timezone

from app.db import SessionLocal
from app.models import Patient, MedicalRecord
from app.security_crypto import encrypt_value, decrypt_value


def _patient_dict(patient):
    profile = decrypt_value(
        patient.encrypted_profile
    )

    return {
        "id": patient.id,
        **profile,
        "records": [
            {
                "id": record.id,
                "record_type": record.record_type,
                "content": decrypt_value(
                    record.encrypted_content
                ),
                "record_date": (
                    record.record_date.isoformat()
                    if record.record_date
                    else None
                ),
            }
            for record in sorted(
                patient.records,
                key=lambda r: r.record_date,
                reverse=True,
            )
        ],
    }


def create_patient(profile=None):
    profile = profile or {}

    db = SessionLocal()

    try:
        patient = Patient(
            encrypted_profile=encrypt_value(profile)
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)

        return _patient_dict(patient)

    finally:
        db.close()


def load_patient(patient_id):
    db = SessionLocal()

    try:
        patient = (
            db.query(Patient)
            .filter(Patient.id == patient_id)
            .first()
        )

        if not patient:
            return None

        return _patient_dict(patient)

    finally:
        db.close()


def add_record(patient, record):
    patient_id = patient["id"]

    db = SessionLocal()

    try:
        db_patient = (
            db.query(Patient)
            .filter(Patient.id == patient_id)
            .first()
        )

        if not db_patient:
            return None

        record_date = datetime.now(
            timezone.utc
        )

        db_record = MedicalRecord(
            patient_id=patient_id,
            record_type=record.get(
                "record_type",
                "unknown"
            ),
            encrypted_content=encrypt_value(
                {
                    "title": record.get("title"),
                    "content": record.get("content"),
                }
            ),
            record_date=record_date,
        )

        db.add(db_record)

        db_patient.updated_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(db_record)

        return _patient_dict(db_patient)

    finally:
        db.close()
