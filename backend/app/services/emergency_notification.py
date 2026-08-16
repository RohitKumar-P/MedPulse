
from datetime import datetime, timezone


def build_emergency_notification(
    contact_name,
    patient_name,
    emergency_type,
    latitude,
    longitude,
    hospital_name=None,
    hospital_distance_km=None,
):
    now = datetime.now(timezone.utc).isoformat()

    message = (
        f"MedPulse emergency alert: {patient_name} "
        f"may require immediate medical attention. "
        f"Detected condition: {emergency_type}. "
    )

    if hospital_name:
        message += (
            f"Nearest suitable hospital: {hospital_name}"
        )

        if hospital_distance_km is not None:
            message += (
                f" ({hospital_distance_km} km away)."
            )

    message += (
        f" Location: https://www.google.com/maps/"
        f"search/?api=1&query={latitude},{longitude}"
    )

    return {
        "recipient": contact_name,
        "message": message,
        "created_at": now,
        "status": "pending_user_confirmation"
    }


def notification_requires_confirmation():
    return {
        "required": True,
        "reason":
            "MedPulse requires explicit user/device permission "
            "before sending an emergency notification."
    }
