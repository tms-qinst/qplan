"""Schedule service - orchestrates CPM calculation and persists results."""

import logging
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.scheduling.engine import CPMEngine
from app.models.activity import Activity
from app.models.activity_relationship import ActivityRelationship
from app.models.activity_constraint import ActivityConstraint
from app.models.calendar import Calendar
from app.models.project import Project
from app.schemas.schemas import ScheduleResponse, ScheduleActivityResult

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service for running CPM schedule calculations."""

    def __init__(self, db: Session):
        self.db = db

    def run_schedule(
        self,
        project_id: str,
        data_date: date,
        mode: str = "recalculate",
        ignore_actuals_before: Optional[date] = None,
    ) -> ScheduleResponse:
        """Run CPM scheduling for a project.

        Uses SQLAlchemy Core / raw queries for performance.
        Does NOT load full ORM objects for CPM computation.
        """
        # Get project calendar
        calendar = (
            self.db.query(Calendar)
            .filter(Calendar.project_id == project_id)
            .first()
        )
        working_days = [1, 2, 3, 4, 5]  # Default Mon-Fri
        holidays = set()

        if calendar:
            if calendar.working_days:
                working_days = calendar.working_days
            if calendar.holidays:
                holidays = {date.fromisoformat(h) for h in calendar.holidays if h}

        # Load activities as flat dictionaries (not ORM objects)
        activities_raw = self.db.execute(
            text("""
                SELECT a.id, a.duration_days, a.status, a.is_milestone,
                       a.actual_start, a.actual_finish,
                       a.remaining_duration_days,
                       a.percent_complete_method,
                       a.duration_percent_complete,
                       ac.constraint_type, ac.constraint_date
                FROM activities a
                LEFT JOIN activity_constraints ac ON ac.activity_id = a.id
                WHERE a.project_id = :project_id
            """),
            {"project_id": project_id},
        ).fetchall()

        activities = []
        for row in activities_raw:
            activities.append({
                "id": row.id,
                "duration_days": float(row.duration_days) if row.duration_days else 0,
                "status": row.status or "not_started",
                "is_milestone": row.is_milestone or False,
                "actual_start": row.actual_start,
                "actual_finish": row.actual_finish,
                "remaining_duration_days": float(row.remaining_duration_days) if row.remaining_duration_days else None,
                "percent_complete_method": row.percent_complete_method or "Duration",
                "duration_percent_complete": float(row.duration_percent_complete) if row.duration_percent_complete else None,
                "constraint_type": row.constraint_type,
                "constraint_date": row.constraint_date,
            })

        # Load relationships as flat dictionaries
        relationships_raw = self.db.execute(
            text("""
                SELECT predecessor_id, successor_id, relationship_type, lag_days
                FROM activity_relationships ar
                JOIN activities a1 ON ar.predecessor_id = a1.id
                JOIN activities a2 ON ar.successor_id = a2.id
                WHERE a1.project_id = :project_id AND a2.project_id = :project_id
            """),
            {"project_id": project_id},
        ).fetchall()

        relationships = []
        for row in relationships_raw:
            relationships.append({
                "predecessor_id": row.predecessor_id,
                "successor_id": row.successor_id,
                "relationship_type": row.relationship_type,
                "lag_days": float(row.lag_days) if row.lag_days else 0,
            })

        # Run CPM engine
        engine = CPMEngine(
            activities=activities,
            relationships=relationships,
            data_date=data_date,
            working_days=working_days,
            holidays=holidays,
        )

        results = engine.run()

        # Persist CPM results back to database
        for result in results:
            self.db.execute(
                text("""
                    UPDATE activities
                    SET early_start = :es, early_finish = :ef,
                        late_start = :ls, late_finish = :lf,
                        total_float = :tf, free_float = :ff,
                        is_critical = :ic,
                        planned_start = COALESCE(planned_start, :es),
                        planned_finish = COALESCE(planned_finish, :ef)
                    WHERE id = :aid
                """),
                {
                    "aid": result["activity_id"],
                    "es": result["early_start"],
                    "ef": result["early_finish"],
                    "ls": result["late_start"],
                    "lf": result["late_finish"],
                    "tf": result["total_float"],
                    "ff": result["free_float"],
                    "ic": result["is_critical"],
                },
            )

        # Update project data_date
        self.db.execute(
            text("UPDATE projects SET data_date = :dd WHERE id = :pid"),
            {"dd": data_date, "pid": project_id},
        )

        self.db.commit()

        # Build response
        return ScheduleResponse(
            project_id=project_id,
            data_date=data_date,
            activities=[ScheduleActivityResult(**r) for r in results],
            critical_path=engine.critical_path,
            warnings=engine.warnings,
        )