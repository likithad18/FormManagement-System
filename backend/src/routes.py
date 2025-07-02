from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas, deps
from .schemas import PaginatedSubmissions

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

@router.get("/", response_model=PaginatedSubmissions)
def list_submissions(
    skip: int = Query(0, description="Number of records to skip (offset)"),
    limit: int = Query(20, description="Number of records per page"),
    search: str = Query(None, description="Search by name or email"),
    db: Session = Depends(deps.get_db)
):
    return crud.get_submissions(db, skip=skip, limit=limit, search=search)

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