from fastapi import APIRouter, Query
from app.services.evidence_engine import search_clinical_trials


router = APIRouter(
    prefix="/research",
    tags=["Clinical Research"]
)


@router.get("/trials")
async def clinical_trials(
    condition: str = Query(
        ...,
        min_length=2,
        max_length=200
    )
):

    result = await search_clinical_trials(
        condition
    )

    return {
        "query": condition,
        "available": result["available"],
        "error": result["error"],
        "count": len(result["studies"]),
        "studies": result["studies"],
        "policy": {
            "recommendation": False,
            "eligibility_confirmation": False,
            "official_record_required": True
        }
    }
