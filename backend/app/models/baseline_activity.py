"""Baseline activity snapshot model."""

import uuid
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BaselineActivity(Base):
    __tablename__ = "baseline_activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    baseline_id = Column(String(36), ForeignKey("baselines.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(String(36), ForeignKey("activities.id"), nullable=False, index=True)
    baseline_start = Column(Date, nullable=False)
    baseline_finish = Column(Date, nullable=False)
    baseline_duration = Column(Numeric(10, 2), nullable=False)
    baseline_percent_complete_method = Column(String(50), default="Duration")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    baseline = relationship("Baseline", back_populates="baseline_activities")
    activity = relationship("Activity")