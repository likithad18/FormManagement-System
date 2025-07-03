from dotenv import load_dotenv; load_dotenv()
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE",
    "sqlite:///:memory:"
)

# SQLALCHEMY_DATABASE_URL = "postgresql://formuser:lalithaAWSpassword123@formdb.cv84o8iymmz6.us-east-2.rds.amazonaws.com:5432/formdb"

# DATABASE=postgresql://formuser:lalithaAWSpassword123@formdb.cv84o8iymmz6.us-east-2.rds.amazonaws.com:5432/formdb 

# Use connect_args only for SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 