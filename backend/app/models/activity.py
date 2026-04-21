"""Activity model."""

import uuid
from sqlalchemy import Column, String, Numeric, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    wbs_id = Column(String(36), ForeignKey("wbs.id"), nullable=False, index=True)
    activity_code = Column(String(100), nullable=False)
    activity_name = Column(String(255), nullable=False)
    activity_type = Column(String(50), default="task")  # task, milestone, level_of_effort
    duration_days = Column(Numeric(10, 2), default=0)
    planned_start = Column(Date, nullable=True)
    planned_finish = Column(Date, nullable=True)
    actual_start = Column(Date, nullable=True)
    actual_finish = Column(Date, nullable=True)
    remaining_duration_days = Column(Numeric(10, 2), nullable=True)
    percent_complete_method = Column(String(50), default="Duration")  # Duration, Physical, Units, LevelOfEffort
    duration_percent_complete = Column(Numeric(5, 2), default=0)
    physical_percent_complete = Column(Numeric(5, 2), default=0)
    units_percent_complete = Column(Numeric(5, 2), default=0)
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed
    is_milestone = Column(Boolean, default=False)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    # CPM calculated fields (updated by scheduling engine)
    early_start = Column(Date, nullable=True)
    early_finish = Column(Date, nullable=True)
    late_start = Column(Date, nullable=True)
    late_finish = Column(Date, nullable=True)
    total_float = Column(Numeric(10, 2), nullable=True)
    free_float = Column(Numeric(10, 2), nullable=True)
    is_critical = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="activities")
    wbs = relationship("WBS", back_populates="activities")
    owner = relationship("User", foreign_keys=[owner_id])
    predecessors = relationship(
        "ActivityRelationship",
        foreign_keys="ActivityRelationship.successor_id",
        back_populates="successor",
        cascade="all, delete-orphan",
    )
    successors = relationship(
        "ActivityRelationship",
        foreign_keys="ActivityRelationship.predecessor_id",
        back_populates="predecessor",
        cascade="all, delete-orphan",
    )
    constraints = relationship("ActivityConstraint", back_populates="activity", cascade="all, delete-orphan")
    code_assignments = relationship("ActivityCodeAssignment", back_populates="activity", cascade="all, delete-orphan")
    progress_updates = relationship("ProgressUpdate", back_populates="activity", cascade="all, delete-orphan")
    resource_assignments = relationship("ResourceAssignment", back_populates="activity", cascade="all, delete-orphan")