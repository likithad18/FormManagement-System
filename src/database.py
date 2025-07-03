import os
import json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import boto3


def get_db_secret():
    secret_arn = os.getenv("SECRETS_MANAGER_ARN")
    if not secret_arn:
        return {
            "username": os.getenv("DB_USER", "formuser"),
            "password": os.getenv("DB_PASSWORD", ""),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "dbname": os.getenv("DB_NAME", "formdb")
        }
    client = boto3.client('secretsmanager', region_name=os.getenv("AWS_REGION", "us-east-2"))
    response = client.get_secret_value(SecretId=secret_arn)
    return json.loads(response['SecretString'])

def get_db_url():
    secret = get_db_secret()
    return f"postgresql+psycopg2://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbname']}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", get_db_url())
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() 