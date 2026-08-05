from typing import Optional
from pydantic import BaseModel

from app.schemas.common import BaseSchema

class PatientCreate(BaseSchema):
    first_name: str
    last_name: str
    phone: Optional[str] = None

class PatientOut(BaseSchema):
    id: int
    first_name: str
    last_name: str
    phone: Optional[str] = None