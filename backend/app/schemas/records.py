from pydantic import BaseModel
from typing import Optional


class MedicalRecord(BaseModel):

    title: str
    record_type: str
    record_date: Optional[str] = None
    source: Optional[str] = None
    extracted_text: Optional[str] = None
