import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, String

from helix_platform.persistence import Base


class IssueDB(Base):
    """SQLAlchemy model representing persistent Issue state."""

    __tablename__ = "issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    citizen_id = Column(String(36), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2048), nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="INTAKE")
    priority = Column(String(50), nullable=False, default="LOW")
    location_address = Column(String(505), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    department_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))


class RecommendationDB(Base):
    """SQLAlchemy model representing persistent AI Recommendation state."""

    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String(36), nullable=False)
    suggested_category = Column(String(50), nullable=False)
    suggested_department = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    rationale = Column(String(2048), nullable=False)
    status = Column(String(50), nullable=False, default="PROPOSED")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
