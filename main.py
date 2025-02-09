import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from passlib.context import CryptContext

from database import SessionLocal, engine, Base
from models import User, Document, Activity
from schemas import UserCreate, UserLogin, UserResponse, UserUpdate, DocumentSchema, ActivitySchema
from crud import create_user, get_user_by_email, update_user_profile, create_document, get_documents_by_user, create_activity, get_activities_by_user

# Crear las tablas (esto actualizará la base de datos según los modelos actuales)
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "https://javierbuenopatience.github.io",
    "https://javierbuenopatience.github.io/Patience",
    "http://127.0.0.1:8000",
    "https://javierbuenopatience.github.io/Patiencefrontend/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Patience"}

@app.post("/users/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    return create_user(db=db, user=user)

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

@app.get("/profile", response_model=UserResponse)
def get_profile(user_email: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user_email)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@app.post("/profile", response_model=UserResponse)
def update_profile(user_email: str, profile: UserUpdate, db: Session = Depends(get_db)):
    updated_user = update_user_profile(db, user_email, profile.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return updated_user

@app.post("/uploadfile", response_model=DocumentSchema)
async def upload_file(user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Directorio donde se almacenarán los archivos
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    # Para el MVP, usaremos la ruta local como URL; en producción, se debería usar una URL pública (p.ej., S3)
    file_url = file_location
    document = create_document(db, user_email, file.filename, file_url, file.content_type)
    return document

@app.get("/documents", response_model=List[DocumentSchema])
def list_documents(user_email: str, db: Session = Depends(get_db)):
    docs = get_documents_by_user(db, user_email)
    return docs

@app.get("/activities", response_model=List[ActivitySchema])
def list_activities(user_email: str, db: Session = Depends(get_db)):
    activities = get_activities_by_user(db, user_email)
    return activities

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
