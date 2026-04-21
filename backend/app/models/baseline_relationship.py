"""Baseline relationship snapshot model."""

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BaselineRelationship(Base):
    __tablename__ = "baseline_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    baseline_id = Column(String(36), ForeignKey("baselines.id", ondelete="CASCADE"), nullable=False, index=True)
    predecessor_activity_id = Column(String(36), ForeignKey("activities.id"), nullable=False)
    successor_activity_id = Column(String(36), ForeignKey("activities.id"), nullable=False)
    relationship_type = Column(String(10), nullable=False)  # FS, SS, FF, SF
    lag_days = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    baseline = relationship("Baseline", back_populates="baseline_relationships")
    predecessor_activity = relationship("Activity", foreign_keys=[predecessor_activity_id])
    successor_activity = relationship("Activity", foreign_keys=[successor_activity_id])