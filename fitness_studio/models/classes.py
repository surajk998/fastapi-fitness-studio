from datetime import time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CourseUserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_encoders={time: lambda t: t.isoformat()}
    )

    id: int
    user_id: int
    course_id: int
    course_name: str
    course_description: str
    course_timing: time
    booked_slot: Optional[int] = 0


class CourseInstructor(CourseUserOut):
    instructor_name: str


class CourseUser(CourseUserOut):
    user_name: str
