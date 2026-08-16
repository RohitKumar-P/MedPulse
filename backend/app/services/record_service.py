from datetime import datetime, timezone

from app.db import SessionLocal
from app.models import Patient, MedicalRecord
from app.security_crypto import encrypt_value, decrypt_value


def save_record(record):
    patient_id = record.get("patient_id")

    if not patient_id:
        raise ValueError("patient_id is required")

    db = SessionLocal()

    try:
        patient = (
            db.query(Patient)
            .filter(Patient.id == patient_id)
            .first()
        )

        if not patient:
            raise ValueError("Patient not found")

        db_record = MedicalRecord(
            patient_id=patient_id,
            record_type=record.get(
                "record_type",
                "unknown"
            ),
            encrypted_content=encrypt_value({
                "title": record.get("title"),
                "content": record.get("content"),
                "source": record.get("source"),
                "metadata": record.get("metadata"),
            }),
            record_date=datetime.now(timezone.utc),
        )

        db.add(db_record)

        patient.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_record)

        return {
            "id": db_record.id,
            "patient_id": db_record.patient_id,
            "record_type": db_record.record_type,
            "record_date": db_record.record_date.isoformat(),
            "content": decrypt_value(
                db_record.encrypted_content
            ),
        }

    finally:
        db.close()


def list_records(patient_id=None):
    db = SessionLocal()

    try:
        query = db.query(MedicalRecord)

        if patient_id:
            query = query.filter(
                MedicalRecord.patient_id == patient_id
            )

        records = query.order_by(
            MedicalRecord.record_date.desc()
        ).all()

        return [
            {
                "id": record.id,
                "patient_id": record.patient_id,
                "record_type": record.record_type,
                "record_date": (
                    record.record_date.isoformat()
                    if record.record_date
                    else None
                ),
                "content": decrypt_value(
                    record.encrypted_content
                ),
            }
            for record in records
        ]

    finally:
        db.close()
