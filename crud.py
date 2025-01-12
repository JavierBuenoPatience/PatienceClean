from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import User
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
