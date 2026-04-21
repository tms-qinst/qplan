"""Activity constraint model."""

import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ActivityConstraint(Base):
    __tablename__ = "activity_constraints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    constraint_type = Column(String(50), nullable=False)
    # Types: must_start_on, must_finish_on, start_no_earlier_than, finish_no_later_than
    constraint_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    activity = relationship("Activity", back_populates="constraints")