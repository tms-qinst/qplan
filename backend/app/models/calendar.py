"""Calendar model."""

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Calendar(Base):
    __tablename__ = "calendars"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    calendar_name = Column(String(255), nullable=False)
    working_days = Column(JSON, default=list)  # e.g. [1, 2, 3, 4, 5] for Mon-Fri
    holidays = Column(JSON, default=list)  # e.g. ["2026-01-01", "2026-12-25"]
    daily_hours = Column(Numeric(4, 2), default=8.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="calendars")