from fastapi import APIRouter

from app.schemas.assessment import (
    SymptomAssessment
)

from app.services.symptom_engine import (
    analyze_symptoms
)

from app.services.report_engine import (
    plain_language_report,
    detailed_report
)


router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"]
)


@router.post("/symptoms")
async def symptom_assessment(
    data: SymptomAssessment
):

    return await analyze_symptoms(
        data.symptoms
    )


@router.post("/report/plain")
async def plain_report(
    data: SymptomAssessment
):

    assessment = await analyze_symptoms(
        data.symptoms
    )

    return plain_language_report(
        assessment
    )


@router.post("/report/detailed")
async def technical_report(
    data: SymptomAssessment
):

    assessment = await analyze_symptoms(
        data.symptoms
    )

    return detailed_report(
        assessment
    )
