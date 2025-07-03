from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas, deps
from .schemas import PaginatedSubmissions
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from .auth import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token, oauth2_scheme
import boto3
import os
from sqlalchemy import func
from .deps import limiter

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
SES_EMAIL_FROM = os.getenv("SES_EMAIL_FROM")
SES_EMAIL_TO = os.getenv("SES_EMAIL_TO")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
ses_client = boto3.client(
    "ses",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

@router.get("/", response_model=PaginatedSubmissions)
def list_submissions(
    skip: int = Query(0, description="Number of records to skip (offset)"),
    limit: int = Query(20, description="Number of records per page"),
    search: str = Query(None, description="Search by name or email"),
    age: int = Query(None, description="Filter by age"),
    preferred_contact: str = Query(None, description="Filter by preferred contact"),
    created_from: str = Query(None, description="Created from date (YYYY-MM-DD)"),
    created_to: str = Query(None, description="Created to date (YYYY-MM-DD)"),
    sort_by: str = Query(None, description="Sort by field (created_at, full_name, age)"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    db: Session = Depends(deps.get_db)
):
    return crud.get_submissions(db, skip=skip, limit=limit, search=search, age=age, preferred_contact=preferred_contact, created_from=created_from, created_to=created_to, sort_by=sort_by, sort_order=sort_order)

@router.get("/{submission_id}", response_model=schemas.SubmissionOut)
def get_submission(submission_id: int, db: Session = Depends(deps.get_db)):
    submission = crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.post("/", response_model=schemas.SubmissionOut, status_code=status.HTTP_201_CREATED)
def create_submission(submission: schemas.SubmissionCreate, db: Session = Depends(deps.get_db)):
    return crud.create_submission(db, submission)

@router.put("/{submission_id}", response_model=schemas.SubmissionOut)
def update_submission(submission_id: int, submission: schemas.SubmissionUpdate, db: Session = Depends(deps.get_db)):
    updated = crud.update_submission(db, submission_id, submission)
    if not updated:
        raise HTTPException(status_code=404, detail="Submission not found")
    return updated

@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(submission_id: int, db: Session = Depends(deps.get_db)):
    deleted = crud.delete_submission(db, submission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Submission not found")
    return None

# Dummy user for demonstration
fake_user = {
    "username": "testuser",
    "hashed_password": get_password_hash("testpass")
}

@router.post("/api/auth/token")
def login(form_data: dict = Body(...)):
    username = form_data.get("username")
    password = form_data.get("password")
    if username != fake_user["username"] or not verify_password(password, fake_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": username})
    refresh_token = create_refresh_token({"sub": username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/api/auth/refresh")
def refresh_token(refresh_token: str = Body(...)):
    payload = decode_token(refresh_token)
    username = payload.get("sub")
    access_token = create_access_token({"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/api/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    return {"user": payload["sub"], "message": "You are authenticated."}

# Example rate-limited endpoint
@router.get("/api/limited")
@limiter.limit("5/minute")
def limited_endpoint(request: Request):
    return {"message": "This endpoint is rate limited to 5 requests per minute."}

@router.post("/api/upload")
def upload_file(file: UploadFile = File(...)):
    key = f"uploads/{file.filename}"
    s3_client.upload_fileobj(file.file, S3_BUCKET, key)
    file_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    # Send email notification
    if SES_EMAIL_FROM and SES_EMAIL_TO:
        ses_client.send_email(
            Source=SES_EMAIL_FROM,
            Destination={"ToAddresses": [SES_EMAIL_TO]},
            Message={
                "Subject": {"Data": "File Uploaded"},
                "Body": {"Text": {"Data": f"File uploaded: {file_url}"}}
            }
        )
    return {"file_url": file_url}

@router.get("/api/analytics")
def get_analytics(db: Session = Depends(deps.get_db)):
    from .models import Submission
    total = db.query(Submission).count()
    by_day = db.query(func.date(Submission.created_at), func.count()).group_by(func.date(Submission.created_at)).all()
    return {"total": total, "by_day": by_day} 