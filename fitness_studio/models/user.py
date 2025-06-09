from datetime import date

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    age: int
    contact_number: int
    emergency_contact_number: int
    address: str
    date_of_birth: date
    joining_date: date = Field(date.today())
    instructor: bool = Field(False)


class UserIn(User):
    password: SecretStr = Field(alias="password", min_length=8, exclude=True)
