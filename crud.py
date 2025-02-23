from sqlalchemy.orm import Session # type: ignore
from passlib.context import CryptContext # type: ignore

from models import User, Document, Activity
from schemas import UserCreate

# Configuración de passlib para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user: UserCreate):
    hashed_pw = pwd_context.hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def update_user_profile(db: Session, user_email: str, profile_data: dict):
    db_user = get_user_by_email(db, email=user_email)
    if not db_user:
        return None
    db_user.name = profile_data.get("name", db_user.name)
    db_user.phone = profile_data.get("phone", db_user.phone)
    db_user.exam_date = profile_data.get("exam_date", db_user.exam_date)
    db_user.specialty = profile_data.get("specialty", db_user.specialty)
    db_user.hobbies = profile_data.get("hobbies", db_user.hobbies)
    db_user.location = profile_data.get("location", db_user.location)
    db_user.profile_image = profile_data.get("profile_image", db_user.profile_image)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_document(db: Session, user_email: str, filename: str, file_url: str, file_type: str):
    db_document = Document(
        user_email=user_email,
        filename=filename,
        file_url=file_url,
        file_type=file_type
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_documents_by_user(db: Session, user_email: str):
    return db.query(Document).filter(Document.user_email == user_email).all()

def create_activity(db: Session, user_email: str, message: str):
    db_activity = Activity(
        user_email=user_email,
        message=message
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activities_by_user(db: Session, user_email: str):
    return db.query(Activity).filter(Activity.user_email == user_email).all()
