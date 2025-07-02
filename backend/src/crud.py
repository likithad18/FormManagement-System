from sqlalchemy.future import select
from sqlalchemy.orm import Session
from .models import Submission
from .schemas import SubmissionCreate, SubmissionUpdate
from sqlalchemy import or_, func
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def get_submission(db: Session, submission_id: int):
    result = db.execute(select(Submission).where(Submission.id == submission_id))
    return result.scalar_one_or_none()

def get_submissions(db: Session, skip: int = 0, limit: int = 20, search: str = None):
    query = select(Submission)
    if search:
        query = query.where(
            or_(
                Submission.full_name.ilike(f"%{search}%"),
                Submission.email.ilike(f"%{search}%")
            )
        )
    total_query = select(func.count()).select_from(query.subquery())
    total = db.execute(total_query).scalar()
    query = query.order_by(Submission.id.desc())
    result = db.execute(query.offset(skip).limit(limit))
    return {"total": total, "items": result.scalars().all()}

def create_submission(db: Session, submission: SubmissionCreate):
    # Check for duplicate email
    existing = db.execute(select(Submission).where(Submission.email == submission.email)).first()
    if existing:
        print(f"Duplicate email detected: {submission.email}")
        raise HTTPException(status_code=400, detail={"detail": "Duplicate email"})
    print(f"Creating submission with data: {submission.dict()}")
    db_submission = Submission(**submission.dict())
    db.add(db_submission)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError: {e}")
        raise HTTPException(status_code=400, detail={"detail": "Duplicate email"})
    db.refresh(db_submission)
    print(f"Submission created: {db_submission}")
    return db_submission

def update_submission(db: Session, submission_id: int, submission: SubmissionUpdate):
    db_submission = db.execute(select(Submission).where(Submission.id == submission_id)).scalar_one_or_none()
    if db_submission is None:
        return None
    # Check for duplicate email, excluding the current submission
    existing = db.execute(
        select(Submission).where(Submission.email == submission.email, Submission.id != submission_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail={"detail": "Duplicate email"})
    for key, value in submission.dict().items():
        setattr(db_submission, key, value)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def delete_submission(db: Session, submission_id: int):
    db_submission = db.execute(select(Submission).where(Submission.id == submission_id)).scalar_one_or_none()
    if db_submission is None:
        return None
    db.delete(db_submission)
    db.commit()
    return db_submission 