from datetime import time

from pydantic import BaseModel, ConfigDict


class Course(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_encoders={time: lambda t: t.isoformat()})

    id: int
    name: str
    slot: int
    description: str
    timing: time
