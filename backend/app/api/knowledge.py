from fastapi import APIRouter

from app.services.condition_registry import (
    list_conditions
)

from app.knowledge.clinical_knowledge import (
    CLINICAL_KNOWLEDGE
)


router = APIRouter(
    prefix="/knowledge",
    tags=["Medical Knowledge"]
)


@router.get("/conditions")
def conditions():

    conditions = list_conditions()

    return {

        "status":
            "success",

        "total":
            len(conditions),

        "categories": {},

        "conditions":
            conditions,

        "knowledge_coverage": {

            "total_conditions":
                len(conditions),

            "curated_conditions":
                len(CLINICAL_KNOWLEDGE),

            "pending_curation":
                max(
                    0,
                    len(conditions)
                    - len(CLINICAL_KNOWLEDGE)
                )
        }
    }


@router.get("/curated")
def curated():

    return {

        "status":
            "success",

        "total":
            len(
                CLINICAL_KNOWLEDGE
            ),

        "conditions":
            CLINICAL_KNOWLEDGE
    }
