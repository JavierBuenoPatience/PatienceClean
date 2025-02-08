import os
from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from database import SessionLocal, engine, Base
from models import User
from schemas import UserCreate, UserLogin, UserResponse, UserProfileUpdate
from crud import create_user, get_user_by_email

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de CORS
origins = [
    "https://javierbuenopatience.github.io",
    "https://javierbuenopatience.github.io/Patience",
    "http://127.0.0.1:8000",
    "https://javierbuenopatience.github.io/Patiencefrontend/"
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

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Patience"}

# Endpoint para registrar usuarios
@app.post("/users/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    return create_user(db=db, user=user)

# Endpoint para iniciar sesión (login)
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
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone,
            "exam_date": db_user.exam_date,
            "specialty": db_user.specialty,
            "hobbies": db_user.hobbies,
            "location": db_user.location,
            "profile_image": db_user.profile_image
        }
    }

# Endpoint para obtener el perfil del usuario
@app.get("/profile", response_model=UserResponse)
def get_profile(email: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

# Endpoint para actualizar el perfil del usuario
@app.put("/profile", response_model=UserResponse)
def update_profile(email: str = Body(...), profile: UserProfileUpdate = Body(...), db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if profile.name is not None:
        db_user.name = profile.name
    if profile.phone is not None:
        db_user.phone = profile.phone
    if profile.exam_date is not None:
        db_user.exam_date = profile.exam_date
    if profile.specialty is not None:
        db_user.specialty = profile.specialty
    if profile.hobbies is not None:
        db_user.hobbies = profile.hobbies
    if profile.location is not None:
        db_user.location = profile.location
    if profile.profile_image is not None:
        db_user.profile_image = profile.profile_image
    db.commit()
    db.refresh(db_user)
    return db_user

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
