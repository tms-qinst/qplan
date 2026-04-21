"""WBS model."""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class WBS(Base):
    __tablename__ = "wbs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String(36), ForeignKey("wbs.id"), nullable=True)
    wbs_code = Column(String(100), nullable=False)
    wbs_name = Column(String(255), nullable=False)
    level = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="wbs_nodes")
    parent = relationship("WBS", remote_side=[id], backref="children")
    activities = relationship("Activity", back_populates="wbs")