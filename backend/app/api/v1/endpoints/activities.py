"""Activity endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, check_project_membership
from app.models.user import User
from app.models.activity import Activity
from app.models.activity_constraint import ActivityConstraint
from app.models.activity_code_assignment import ActivityCodeAssignment
from app.services.audit_service import AuditService
from app.schemas.schemas import (
    ActivityCreate, ActivityUpdate, ActivityResponse,
    ActivityConstraintCreate, ActivityConstraintResponse,
    ActivityCodeAssignmentCreate, ActivityCodeAssignmentResponse,
)

router = APIRouter(prefix="/projects/{project_id}/activities", tags=["Activities"])


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    project_id: str,
    data: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    activity = Activity(
        project_id=project_id, wbs_id=data.wbs_id,
        activity_code=data.activity_code, activity_name=data.activity_name,
        activity_type=data.activity_type, duration_days=data.duration_days,
        planned_start=data.planned_start, planned_finish=data.planned_finish,
        actual_start=data.actual_start, actual_finish=data.actual_finish,
        remaining_duration_days=data.remaining_duration_days,
        percent_complete_method=data.percent_complete_method,
        duration_percent_complete=data.duration_percent_complete,
        physical_percent_complete=data.physical_percent_complete,
        units_percent_complete=data.units_percent_complete,
        status=data.status, is_milestone=data.is_milestone,
        owner_id=data.owner_id,
    )
    db.add(activity)
    audit = AuditService(db)
    audit.log_change(current_user.id, "activity", activity.id, "create", new_value=data.model_dump())
    db.commit()
    db.refresh(activity)
    return activity


@router.get("", response_model=List[ActivityResponse])
def list_activities(
    project_id: str,
    wbs_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    query = db.query(Activity).filter(Activity.project_id == project_id)
    if wbs_id:
        query = query.filter(Activity.wbs_id == wbs_id)
    if status_filter:
        query = query.filter(Activity.status == status_filter)
    return query.order_by(Activity.activity_code).all()


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    project_id: str,
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    activity = db.query(Activity).filter(Activity.id == activity_id, Activity.project_id == project_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    project_id: str,
    activity_id: str,
    data: ActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    activity = db.query(Activity).filter(Activity.id == activity_id, Activity.project_id == project_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    update_data = data.model_dump(exclude_unset=True)
    old_values = {}
    for key, value in update_data.items():
        old_values[key] = getattr(activity, key)
        setattr(activity, key, value)
    audit = AuditService(db)
    audit.log_change(current_user.id, "activity", activity.id, "update", old_value=old_values, new_value=update_data)
    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    project_id: str,
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    activity = db.query(Activity).filter(Activity.id == activity_id, Activity.project_id == project_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    audit = AuditService(db)
    audit.log_change(current_user.id, "activity", activity.id, "delete", old_value={"activity_code": activity.activity_code})
    db.delete(activity)
    db.commit()


# ─── Activity Constraints ───────────────────────────────

@router.post("/{activity_id}/constraints", response_model=ActivityConstraintResponse, status_code=status.HTTP_201_CREATED)
def add_constraint(
    project_id: str,
    activity_id: str,
    data: ActivityConstraintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    activity = db.query(Activity).filter(Activity.id == activity_id, Activity.project_id == project_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    constraint = ActivityConstraint(activity_id=activity_id, constraint_type=data.constraint_type, constraint_date=data.constraint_date)
    db.add(constraint)
    db.commit()
    db.refresh(constraint)
    return constraint


@router.get("/{activity_id}/constraints", response_model=List[ActivityConstraintResponse])
def list_constraints(
    project_id: str,
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    return db.query(ActivityConstraint).filter(ActivityConstraint.activity_id == activity_id).all()


# ─── Activity Code Assignments ──────────────────────────

@router.post("/{activity_id}/codes", response_model=ActivityCodeAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_code(
    project_id: str,
    activity_id: str,
    data: ActivityCodeAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    activity = db.query(Activity).filter(Activity.id == activity_id, Activity.project_id == project_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    assignment = ActivityCodeAssignment(activity_id=activity_id, activity_code_id=data.activity_code_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/{activity_id}/codes", response_model=List[ActivityCodeAssignmentResponse])
def list_codes(
    project_id: str,
    activity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    return db.query(ActivityCodeAssignment).filter(ActivityCodeAssignment.activity_id == activity_id).all()