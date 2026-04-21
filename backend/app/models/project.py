"""Project model."""

import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_code = Column(String(100), unique=True, nullable=False, index=True)
    project_name = Column(String(255), nullable=False)
    client_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    project_status = Column(String(50), default="planning")
    start_date = Column(Date, nullable=True)
    finish_date = Column(Date, nullable=True)
    data_date = Column(Date, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    calendars = relationship("Calendar", back_populates="project", cascade="all, delete-orphan")
    wbs_nodes = relationship("WBS", back_populates="project", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="project", cascade="all, delete-orphan")
    baselines = relationship("Baseline", back_populates="project", cascade="all, delete-orphan")
    activity_codes = relationship("ActivityCode", back_populates="project", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="project", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="project", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="project", cascade="all, delete-orphan")