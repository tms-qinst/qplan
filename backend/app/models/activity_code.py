"""Activity code model."""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ActivityCode(Base):
    __tablename__ = "activity_codes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    code_type = Column(String(100), nullable=False)  # Phase, Discipline, Area, etc.
    code_value = Column(String(100), nullable=False)
    code_description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="activity_codes")
    assignments = relationship("ActivityCodeAssignment", back_populates="activity_code", cascade="all, delete-orphan")