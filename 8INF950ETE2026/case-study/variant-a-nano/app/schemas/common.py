from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class DateRangeQuery(BaseModel):
    from_: datetime | None = None
    to: datetime | None = None