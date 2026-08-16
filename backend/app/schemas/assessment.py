from pydantic import BaseModel, Field


class SymptomAssessment(BaseModel):

    symptoms: str = Field(
        min_length=1,
        max_length=5000
    )
