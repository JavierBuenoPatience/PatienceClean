from sqlalchemy import Column, Integer, String, Date
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    exam_date = Column(Date, nullable=True)
    specialty = Column(String, nullable=True)
    hobbies = Column(String, nullable=True)
    location = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
