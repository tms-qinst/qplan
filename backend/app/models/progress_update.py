"""Progress update model."""

import uuid
from sqlalchemy import Column, String, Numeric, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProgressUpdate(Base):
    __tablename__ = "progress_updates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    data_date = Column(Date, nullable=False)
    actual_start = Column(Date, nullable=True)
    actual_finish = Column(Date, nullable=True)
    remaining_duration_days = Column(Numeric(10, 2), nullable=True)
    duration_percent_complete = Column(Numeric(5, 2), nullable=True)
    physical_percent_complete = Column(Numeric(5, 2), nullable=True)
    units_percent_complete = Column(Numeric(5, 2), nullable=True)
    remarks = Column(Text, nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    activity = relationship("Activity", back_populates="progress_updates")
    updater = relationship("User", foreign_keys=[updated_by])