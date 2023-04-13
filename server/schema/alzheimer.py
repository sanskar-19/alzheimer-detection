from pydantic import BaseModel, EmailStr
from fastapi import File, UploadFile


class AlzheimerForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    gender: str
    age: int
