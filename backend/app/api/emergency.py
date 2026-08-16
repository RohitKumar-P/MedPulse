from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.ai.critical_symptoms import detect_critical_symptoms
from app.services.hospital_service import nearby_hospitals
from app.db import SessionLocal
from app.api.emergency_contacts import get_notification_targets
from app.api.auth import get_current_user


router = APIRouter(
    prefix="/emergency",
    tags=["Emergency"]
)


class EmergencyCheckRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000
    )

    latitude: float | None = Field(
        None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        None,
        ge=-180,
        le=180
    )

    accuracy: float | None = Field(
        None,
        ge=0
    )

    critical_response_enabled: bool = False


def validate_location(request):

    supplied = (
        request.latitude is not None
        or request.longitude is not None
        or request.accuracy is not None
    )

    if not supplied:
        return False

    if (
        request.latitude is None
        or request.longitude is None
        or request.accuracy is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Complete device location is required."
        )

    if request.accuracy > 5000:
        raise HTTPException(
            status_code=400,
            detail="Device location accuracy is too low."
        )

    return True


@router.post("/check")
async def emergency_check(
    request: EmergencyCheckRequest,
    current_user=Depends(get_current_user)
):

    detected = detect_critical_symptoms(
        request.text
    )

    critical = bool(detected)

    response = {
        "status": "success",

        "critical": critical,

        "severity":
            "critical"
            if critical
            else "normal",

        "detected_symptoms":
            detected,

        "location": None,

        "location_required":
            critical,

        "hospital_search": None,

        "recommended_hospitals": [],

        "emergency_contacts": {
            "available": False,
            "count": 0,
            "targets": []
        },

        "emergency_call": {
            "available": False,
            "permission_required": True,
            "auto_call_enabled":
                request.critical_response_enabled
        },

        "actions": []
    }

    if not critical:

        return response

    response["actions"] = [
        "Seek immediate medical attention",
        "View nearby emergency hospitals",
        "Contact emergency services"
    ]

    has_location = validate_location(
        request
    )

    if not has_location:

        response["hospital_search"] = {
            "source":
                "device_gps_required",

            "hospitals": []
        }

        return response

    response["location"] = {
        "latitude":
            request.latitude,

        "longitude":
            request.longitude,

        "accuracy_meters":
            request.accuracy,

        "source":
            "device_gps"
    }

    db = SessionLocal()

    try:
        targets = get_notification_targets(
            str(current_user.id),
            db
        )
    finally:
        db.close()

    response["emergency_contacts"] = {
        "available": bool(targets),
        "count": len(targets),
        "targets": targets
    }

    hospital_data = await nearby_hospitals(
        request.latitude,
        request.longitude,
        10000
    )

    response["hospital_search"] = (
        hospital_data
    )

    response["recommended_hospitals"] = (
        hospital_data.get(
            "hospitals",
            []
        )[:5]
    )

    response["emergency_call"] = {
        "available": True,
        "permission_required": True,
        "auto_call_enabled":
            request.critical_response_enabled
    }

    return response



@router.post("/notify-confirm")
async def confirm_emergency_notification(
    current_user=Depends(get_current_user)
):
    return {
        "status": "confirmation_received",
        "user_id": str(current_user.id),
        "notification": {
            "authorized": True,
            "status": "ready_to_send"
        },
        "message":
            "Emergency notification authorized by the user."
    }


@router.post("/activate")
async def activate_emergency(
    request: EmergencyCheckRequest
):

    detected = detect_critical_symptoms(
        request.text
    )

    if not detected:

        return {
            "status":
                "not_activated",

            "critical":
                False,

            "message":
                "No critical symptoms detected."
        }

    return {
        "status":
            "activated",

        "critical":
            True,

        "message":
            "Emergency mode activated.",

        "detected_symptoms":
            detected,

        "call_permission_required":
            True,

        "location_permission_required":
            True,

        "actions": [
            "Show emergency warning",
            "Request device location",
            "Find nearby suitable hospitals",
            "Offer emergency call",
            "Offer emergency contact notification"
        ]
    }
