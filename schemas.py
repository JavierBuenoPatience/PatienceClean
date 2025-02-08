from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    exam_date: date | None = None
    specialty: str | None = None
    hobbies: str | None = None
    location: str | None = None
    profile_image: str | None = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    exam_date: date | None = None
    specialty: str | None = None
    hobbies: str | None = None
    location: str | None = None
    profile_image: str | None = None

    class Config:
        from_attributes = True
