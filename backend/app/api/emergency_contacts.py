from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db import SessionLocal
from app.models import EmergencyContact
from app.api.auth import get_current_user
from app.security_crypto import encrypt_value, decrypt_value


router = APIRouter(
    prefix="/emergency-contacts",
    tags=["Emergency Contacts"]
)


class EmergencyContactRequest(BaseModel):

    name: str = Field(
        ...,
        min_length=1,
        max_length=120
    )

    phone: str = Field(
        ...,
        min_length=5,
        max_length=30
    )

    relationship: str = Field(
        ...,
        min_length=1,
        max_length=60
    )


def serialize_contact(contact):

    return {
        "id": contact.id,
        "name": contact.name,
        "phone": decrypt_value(
            contact.phone_encrypted
        ),
        "relationship": contact.relationship,
        "created_at": contact.created_at.isoformat()
    }



def get_notification_targets(
    user_id: str,
    db
):
    contacts = db.scalars(
        select(EmergencyContact)
        .where(
            EmergencyContact.user_id == user_id
        )
        .order_by(
            EmergencyContact.created_at
        )
    ).all()

    return [
        {
            "id": contact.id,
            "name": contact.name,
            "relationship": contact.relationship
        }
        for contact in contacts
    ]


def get_contact_phone_for_notification(
    contact_id: str,
    user_id: str,
    db
):
    contact = db.scalar(
        select(EmergencyContact)
        .where(
            EmergencyContact.id == contact_id,
            EmergencyContact.user_id == user_id
        )
    )

    if contact is None:
        return None

    return decrypt_value(
        contact.phone_encrypted
    )


@router.get("")
def list_contacts(
    current_user=Depends(get_current_user)
):

    db = SessionLocal()

    try:

        user_id = str(current_user.id)

        contacts = db.scalars(
            select(EmergencyContact)
            .where(
                EmergencyContact.user_id == user_id
            )
            .order_by(
                EmergencyContact.created_at
            )
        ).all()

        return {
            "status": "success",
            "contacts": [
                serialize_contact(contact)
                for contact in contacts
            ]
        }

    finally:
        db.close()


@router.post("")
def add_contact(
    request: EmergencyContactRequest,
    current_user=Depends(get_current_user)
):

    db = SessionLocal()

    try:

        user_id = str(current_user.id)

        count = db.scalar(
            select(
                EmergencyContact.id
            )
            .where(
                EmergencyContact.user_id == user_id
            )
            .limit(4)
        )

        existing = db.scalars(
            select(EmergencyContact)
            .where(
                EmergencyContact.user_id == user_id
            )
        ).all()

        if len(existing) >= 3:

            raise HTTPException(
                status_code=400,
                detail="Maximum of 3 emergency contacts allowed."
            )

        contact = EmergencyContact(

            user_id=user_id,

            name=request.name.strip(),

            phone_encrypted=encrypt_value(
                request.phone.strip()
            ),

            relationship=request.relationship.strip()
        )

        db.add(contact)
        db.commit()
        db.refresh(contact)

        return {
            "status": "success",
            "contact": serialize_contact(contact)
        }

    except HTTPException:
        raise

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to save emergency contact."
        )

    finally:
        db.close()


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: str,
    current_user=Depends(get_current_user)
):

    db = SessionLocal()

    try:

        user_id = str(current_user.id)

        contact = db.scalar(
            select(EmergencyContact)
            .where(
                EmergencyContact.id == contact_id,
                EmergencyContact.user_id == user_id
            )
        )

        if contact is None:

            raise HTTPException(
                status_code=404,
                detail="Emergency contact not found."
            )

        db.delete(contact)
        db.commit()

        return {
            "status": "success",
            "message":
                "Emergency contact removed."
        }

    except HTTPException:
        raise

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to remove emergency contact."
        )

    finally:
        db.close()
