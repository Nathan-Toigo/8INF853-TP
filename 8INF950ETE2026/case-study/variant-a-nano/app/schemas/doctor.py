from pydantic import BaseModel

from app.schemas.common import BaseSchema

class DoctorOut(BaseSchema):
    id: int
    specialty: str

class DoctorCreate(BaseSchema):
    specialty: str