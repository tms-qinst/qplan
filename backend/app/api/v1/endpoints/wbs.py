"""WBS endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, check_project_membership
from app.models.user import User
from app.models.wbs import WBS
from app.schemas.schemas import WBSCreate, WBSUpdate, WBSResponse

router = APIRouter(prefix="/projects/{project_id}/wbs", tags=["WBS"])


@router.post("", response_model=WBSResponse, status_code=status.HTTP_201_CREATED)
def create_wbs(
    project_id: str,
    data: WBSCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    wbs = WBS(
        project_id=project_id, parent_id=data.parent_id,
        wbs_code=data.wbs_code, wbs_name=data.wbs_name,
        level=data.level, sort_order=data.sort_order,
    )
    db.add(wbs)
    db.commit()
    db.refresh(wbs)
    return wbs


@router.get("", response_model=List[WBSResponse])
def list_wbs(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    nodes = db.query(WBS).filter(WBS.project_id == project_id).order_by(WBS.sort_order).all()
    return nodes


@router.get("/{wbs_id}", response_model=WBSResponse)
def get_wbs(
    project_id: str,
    wbs_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    wbs = db.query(WBS).filter(WBS.id == wbs_id, WBS.project_id == project_id).first()
    if not wbs:
        raise HTTPException(status_code=404, detail="WBS not found")
    return wbs


@router.put("/{wbs_id}", response_model=WBSResponse)
def update_wbs(
    project_id: str,
    wbs_id: str,
    data: WBSUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    wbs = db.query(WBS).filter(WBS.id == wbs_id, WBS.project_id == project_id).first()
    if not wbs:
        raise HTTPException(status_code=404, detail="WBS not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(wbs, key, value)
    db.commit()
    db.refresh(wbs)
    return wbs


@router.delete("/{wbs_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wbs(
    project_id: str,
    wbs_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    wbs = db.query(WBS).filter(WBS.id == wbs_id, WBS.project_id == project_id).first()
    if not wbs:
        raise HTTPException(status_code=404, detail="WBS not found")
    db.delete(wbs)
    db.commit()