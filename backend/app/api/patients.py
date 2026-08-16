from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.api.auth import require_roles

from app.services.patient_store import (
    create_patient,
    load_patient,
    add_record
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


class RecordInput(BaseModel):

    record_type: str

    title: str

    content: str


@router.post("")
def create(current_user=Depends(require_roles("admin", "doctor", "staff"))):

    return create_patient()


@router.get("/{patient_id}")
def get_patient(
    patient_id: str,
    current_user=Depends(require_roles("admin", "doctor", "staff"))
):

    patient = load_patient(
        patient_id
    )

    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


@router.post("/{patient_id}/records")
def add_patient_record(
    patient_id: str,
    record: RecordInput,
    current_user=Depends(require_roles("admin", "doctor", "staff"))
):

    patient = load_patient(
        patient_id
    )

    if not patient:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return add_record(
        patient,
        record.model_dump()
    )
