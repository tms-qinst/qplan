"""Activity relationship endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, check_project_membership
from app.models.user import User
from app.models.activity import Activity
from app.models.activity_relationship import ActivityRelationship
from app.schemas.schemas import ActivityRelationshipCreate, ActivityRelationshipResponse

router = APIRouter(prefix="/projects/{project_id}/relationships", tags=["Relationships"])


@router.post("", response_model=ActivityRelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(
    project_id: str,
    data: ActivityRelationshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    # Validate both activities belong to project
    pred = db.query(Activity).filter(Activity.id == data.predecessor_id, Activity.project_id == project_id).first()
    succ = db.query(Activity).filter(Activity.id == data.successor_id, Activity.project_id == project_id).first()
    if not pred or not succ:
        raise HTTPException(status_code=400, detail="Both activities must belong to the project")
    if data.predecessor_id == data.successor_id:
        raise HTTPException(status_code=400, detail="Cannot create self-referencing relationship")
    if data.relationship_type not in ("FS", "SS", "FF", "SF"):
        raise HTTPException(status_code=400, detail="Invalid relationship type. Must be FS, SS, FF, or SF")
    # Check duplicate
    existing = db.query(ActivityRelationship).filter(
        ActivityRelationship.predecessor_id == data.predecessor_id,
        ActivityRelationship.successor_id == data.successor_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Relationship already exists")
    rel = ActivityRelationship(
        predecessor_id=data.predecessor_id, successor_id=data.successor_id,
        relationship_type=data.relationship_type, lag_days=data.lag_days,
    )
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


@router.get("", response_model=List[ActivityRelationshipResponse])
def list_relationships(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    rels = (
        db.query(ActivityRelationship)
        .join(Activity, ActivityRelationship.predecessor_id == Activity.id)
        .filter(Activity.project_id == project_id)
        .all()
    )
    return rels


@router.delete("/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(
    project_id: str,
    relationship_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    rel = db.query(ActivityRelationship).filter(ActivityRelationship.id == relationship_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db.delete(rel)
    db.commit()