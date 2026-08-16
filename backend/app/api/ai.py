from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.orchestrator import (
    orchestrator
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


class AIInput(BaseModel):

    text: str


@router.post("/extract")
async def extract(
    payload: AIInput
):

    return await orchestrator.extract(
        payload.text
    )
