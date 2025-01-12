import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, engine, Base
from models import User
from schemas import UserCreate, UserResponse
from crud import create_user, get_user_by_email

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de CORS
origins = [
    "https://javierbuenopatience.github.io/Patience/",
    "http://127.0.0.1:8000/", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Puedes usar ["*"] para permitir todos los orígenes
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

@app.post("/users/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Comprueba si el correo ya existe
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    # Crea el usuario
    return create_user(db=db, user=user)

# Configuración para que la app escuche en el puerto especificado por Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Usa el puerto especificado por Railway o 8000 por defecto
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)

