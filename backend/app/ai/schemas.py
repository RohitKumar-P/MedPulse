from pydantic import BaseModel, Field
from typing import Any, List, Optional


class Symptom(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)
    severity: str = "unknown"
    onset: Optional[str] = None
    duration: Optional[str] = None
    current: bool = True
    negated: bool = False


class MedicalExtraction(BaseModel):
    symptoms: List[Symptom] = []
    medications: List[Any] = []
    diagnoses: List[Any] = []
    allergies: List[Any] = []
    laboratory_results: List[Any] = []
    missing_information: List[Any] = []
    uncertainty: List[Any] = []
