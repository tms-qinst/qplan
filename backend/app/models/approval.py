"""Approval model."""

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    approval_type = Column(String(50), nullable=False)  # baseline, schedule_change, etc.
    approval_status = Column(String(50), default="pending")  # pending, approved, rejected
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime(timezone=True), nullable=True)
    remarks = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approved_by])