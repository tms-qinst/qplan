"""Activity relationship (dependency) model."""

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ActivityRelationship(Base):
    __tablename__ = "activity_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    predecessor_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    successor_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(10), nullable=False)  # FS, SS, FF, SF
    lag_days = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    predecessor = relationship(
        "Activity",
        foreign_keys=[predecessor_id],
        back_populates="successors",
    )
    successor = relationship(
        "Activity",
        foreign_keys=[successor_id],
        back_populates="predecessors",
    )