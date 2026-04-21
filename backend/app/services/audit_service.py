"""Audit trail service for tracking entity changes."""

import json
import logging
from typing import Optional

from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for recording audit trail entries."""

    def __init__(self, db: Session):
        self.db = db

    def log_change(
        self,
        user_id: str,
        entity_name: str,
        entity_id: str,
        action_type: str,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
    ):
        """Record an audit log entry."""
        entry = AuditLog(
            user_id=user_id,
            entity_name=entity_name,
            entity_id=entity_id,
            action_type=action_type,
            old_value=old_value,
            new_value=new_value,
        )
        self.db.add(entry)
        # Don't commit here - let the caller manage the transaction