from fastapi import APIRouter, Query, HTTPException
from app.services.hospital_service import nearby_hospitals, get_best_emergency_hospitals

router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"]
)


@router.get("/nearby")
async def get_nearby_hospitals(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    accuracy: float = Query(..., ge=0),
    radius: float = Query(10000, gt=0, le=50000)
):
    if accuracy > 5000:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Location accuracy is too low.",
                "accuracy_meters": accuracy,
                "action": "Request precise device location."
            }
        )

    result = await nearby_hospitals(
        latitude,
        longitude,
        radius
    )

    return {
        "status": "success",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy_meters": accuracy,
            "source": "device_gps"
        },
        **result
    }


@router.get("/location-required")
def location_requirement():
    return {
        "location_required": True,
        "permission_required": True,
        "source": "device_gps",
        "message": "MedPulse requires your location to find nearby hospitals."
    }
