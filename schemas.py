from pydantic import BaseModel, EmailStr # type: ignore
from typing import Optional, List

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
    phone: Optional[str] = None
    exam_date: Optional[str] = None
    specialty: Optional[str] = None
    hobbies: Optional[str] = None
    location: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    exam_date: Optional[str] = None
    specialty: Optional[str] = None
    hobbies: Optional[str] = None
    location: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        orm_mode = True

class DocumentSchema(BaseModel):
    id: int
    user_email: EmailStr
    filename: str
    file_url: str
    file_type: str

    class Config:
        orm_mode = True

class ActivitySchema(BaseModel):
    id: int
    user_email: EmailStr
    message: str

    class Config:
        orm_mode = True
