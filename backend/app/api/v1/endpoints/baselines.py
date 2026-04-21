"""Baseline endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, check_project_membership
from app.models.user import User
from app.models.activity import Activity
from app.models.activity_relationship import ActivityRelationship
from app.models.baseline import Baseline
from app.models.baseline_activity import BaselineActivity
from app.models.baseline_relationship import BaselineRelationship
from app.schemas.schemas import (
    BaselineCreate, BaselineResponse,
    BaselineActivityResponse, BaselineRelationshipResponse,
    ScheduleVarianceReport,
)

router = APIRouter(prefix="/projects/{project_id}/baselines", tags=["Baselines"])


@router.post("", response_model=BaselineResponse, status_code=status.HTTP_201_CREATED)
def create_baseline(
    project_id: str,
    data: BaselineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a baseline snapshot of current activities and relationships."""
    check_project_membership(project_id, current_user, db)

    # Get latest revision number
    latest = db.query(Baseline).filter(Baseline.project_id == project_id).order_by(Baseline.revision_no.desc()).first()
    revision = (latest.revision_no + 1) if latest else 1

    baseline = Baseline(
        project_id=project_id, baseline_name=data.baseline_name,
        revision_no=revision, baseline_type=data.baseline_type,
    )
    db.add(baseline)
    db.flush()

    # Snapshot activities
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    for act in activities:
        ba = BaselineActivity(
            baseline_id=baseline.id, activity_id=act.id,
            baseline_start=act.early_start or act.planned_start,
            baseline_finish=act.early_finish or act.planned_finish,
            baseline_duration=act.duration_days,
            baseline_percent_complete_method=act.percent_complete_method,
        )
        db.add(ba)

    # Snapshot relationships
    rels = (
        db.query(ActivityRelationship)
        .join(Activity, ActivityRelationship.predecessor_id == Activity.id)
        .filter(Activity.project_id == project_id)
        .all()
    )
    for rel in rels:
        br = BaselineRelationship(
            baseline_id=baseline.id,
            predecessor_activity_id=rel.predecessor_id,
            successor_activity_id=rel.successor_id,
            relationship_type=rel.relationship_type,
            lag_days=rel.lag_days,
        )
        db.add(br)

    db.commit()
    db.refresh(baseline)
    return baseline


@router.get("", response_model=List[BaselineResponse])
def list_baselines(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    return db.query(Baseline).filter(Baseline.project_id == project_id).order_by(Baseline.revision_no).all()


@router.get("/{baseline_id}", response_model=BaselineResponse)
def get_baseline(
    project_id: str,
    baseline_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    bl = db.query(Baseline).filter(Baseline.id == baseline_id, Baseline.project_id == project_id).first()
    if not bl:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return bl


@router.get("/{baseline_id}/activities", response_model=List[BaselineActivityResponse])
def get_baseline_activities(
    project_id: str,
    baseline_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    return db.query(BaselineActivity).filter(BaselineActivity.baseline_id == baseline_id).all()


@router.get("/{baseline_id}/relationships", response_model=List[BaselineRelationshipResponse])
def get_baseline_relationships(
    project_id: str,
    baseline_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    return db.query(BaselineRelationship).filter(BaselineRelationship.baseline_id == baseline_id).all()


@router.get("/{baseline_id}/variance", response_model=List[ScheduleVarianceReport])
def get_baseline_variance(
    project_id: str,
    baseline_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compare current schedule vs baseline."""
    check_project_membership(project_id, current_user, db)
    results = db.execute(
        """
        SELECT a.id, a.activity_code, a.activity_name,
               a.early_start as current_start, a.early_finish as current_finish,
               ba.baseline_start, ba.baseline_finish,
               (a.early_start - ba.baseline_start) as start_variance_days,
               (a.early_finish - ba.baseline_finish) as finish_variance_days
        FROM activities a
        JOIN baseline_activities ba ON ba.activity_id = a.id
        WHERE ba.baseline_id = :bid AND a.project_id = :pid
        """,
        {"bid": baseline_id, "pid": project_id},
    ).fetchall()
    return [ScheduleVarianceReport(
        activity_id=r.id, activity_code=r.activity_code, activity_name=r.activity_name,
        current_start=r.current_start, current_finish=r.current_finish,
        baseline_start=r.baseline_start, baseline_finish=r.baseline_finish,
        start_variance_days=r.start_variance_days, finish_variance_days=r.finish_variance_days,
    ) for r in results]


@router.post("/{baseline_id}/approve", response_model=BaselineResponse)
def approve_baseline(
    project_id: str,
    baseline_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    bl = db.query(Baseline).filter(Baseline.id == baseline_id, Baseline.project_id == project_id).first()
    if not bl:
        raise HTTPException(status_code=404, detail="Baseline not found")
    bl.approved_by = current_user.id
    from datetime import datetime
    bl.approved_at = datetime.now()
    db.commit()
    db.refresh(bl)
    return bl