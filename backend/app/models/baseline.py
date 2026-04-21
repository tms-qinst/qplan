"""Baseline model."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    baseline_name = Column(String(255), nullable=False)
    revision_no = Column(Integer, default=1)
    baseline_type = Column(String(50), default="project")  # project, what-if
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="baselines")
    approver = relationship("User", foreign_keys=[approved_by])
    baseline_activities = relationship("BaselineActivity", back_populates="baseline", cascade="all, delete-orphan")
    baseline_relationships = relationship("BaselineRelationship", back_populates="baseline", cascade="all, delete-orphan")