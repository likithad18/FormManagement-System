from sqlalchemy import Column, Integer, String, Text, CheckConstraint, TIMESTAMP, func
from .database import Base

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    address = Column(Text)
    preferred_contact = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint('age >= 18 AND age <= 120', name='age_range'),
        CheckConstraint("preferred_contact IN ('Email', 'Phone', 'Both')", name='preferred_contact_check'),
    ) 