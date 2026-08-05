from datetime import datetime
from pydantic import BaseModel
from app.schemas.common import BaseSchema

class TimeSlotCreate(BaseSchema):
    start_at: datetime
    end_at: datetime

class TimeSlotOut(BaseSchema):
    id: int
    doctor_id: int
    start_at: datetime
    end_at: datetime