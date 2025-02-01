import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Se usa DATABASE_URL si está definida en el entorno; de lo contrario, se usa SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./patience.db")

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print("Database URL:", engine.url)
