import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from database import SessionLocal, engine, Base
from models import User
from schemas import UserCreate, UserLogin, UserResponse
from crud import create_user, get_user_by_email

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de CORS (ajusta los orígenes según tus necesidades)
origins = [
    "https://javierbuenopatience.github.io/Patience/",
    "http://127.0.0.1:8000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # También puedes usar ["*"] para permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para registrar usuarios
@app.post("/users/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Comprueba si el correo ya existe
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    # Crea el usuario y devuelve los datos (sin la contraseña)
    return create_user(db=db, user=user)

# Endpoint para iniciar sesión (login) usando JSON
@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="El correo no está registrado")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    return {
        "message": "Inicio de sesión exitoso",
        "user": {"id": db_user.id, "name": db_user.name, "email": db_user.email}
    }

# Configuración para que la app escuche en el puerto especificado (útil en entornos como Railway o Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
