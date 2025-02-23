import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File # type: ignore
from sqlalchemy.orm import Session # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from typing import List
import boto3 # type: ignore
from botocore.exceptions import NoCredentialsError # type: ignore
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde .env

# Importamos el pwd_context global de crud para reutilizarlo en login
from crud import pwd_context, create_user, get_user_by_email, update_user_profile, create_document, get_documents_by_user, create_activity, get_activities_by_user

from database import SessionLocal, engine, Base
from models import User, Document, Activity
from schemas import UserCreate, UserLogin, UserResponse, UserUpdate, DocumentSchema, ActivitySchema

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
    # Configuración de S3: se leen las variables de entorno
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")
    bucket_name = os.getenv("AWS_S3_BUCKET")
    
    if not all([aws_access_key, aws_secret_key, aws_region, bucket_name]):
        raise HTTPException(status_code=500, detail="Configuración de AWS incompleta")
    
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
    
    try:
        # Subir el archivo a S3
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            file.filename,
            ExtraArgs={"ContentType": file.content_type}
        )
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Error de credenciales de AWS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo: {e}")
    
    # Construir la URL pública del archivo
    file_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{file.filename}"
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
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=port)
