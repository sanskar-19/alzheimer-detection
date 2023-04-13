from pydantic import BaseModel, EmailStr
from ..utils import user as Utiluser
from datetime import datetime


class NewUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class ExistingUser(BaseModel):
    email: EmailStr
    password: str


class NewUserInDb(BaseModel):
    uid: str
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    role: str | None = "admin"
    created_at: datetime
    otp: str
    otp_expiry_at: datetime

    class Config:
        orm_mode = True  # allows the app to take ORM objects and translate them into responses automatically


class UserDetails(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: str | None = "admin"

    class Config:
        orm_mode = True  # allows the app to take ORM objects and translate them into responses automatically


class ResponseModel(BaseModel):
    data: dict
    message: str


class ResetPassword(BaseModel):
    new_password: str
    email: EmailStr
    otp: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str
