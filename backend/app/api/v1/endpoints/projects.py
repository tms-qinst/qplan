"""Project endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, check_project_membership
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.services.audit_service import AuditService
from app.schemas.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectMemberCreate, ProjectMemberResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = Project(
        project_code=data.project_code, project_name=data.project_name,
        client_name=data.client_name, description=data.description,
        project_status=data.project_status, start_date=data.start_date,
        finish_date=data.finish_date, data_date=data.data_date,
        created_by=current_user.id,
    )
    db.add(project)
    db.flush()
    membership = ProjectMember(
        project_id=project.id, user_id=current_user.id, assigned_role="Project Manager",
    )
    db.add(membership)
    audit = AuditService(db)
    audit.log_change(current_user.id, "project", project.id, "create", new_value=data.model_dump())
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = (
        db.query(Project)
        .join(ProjectMember)
        .filter(ProjectMember.user_id == current_user.id)
        .all()
    )
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    update_data = data.model_dump(exclude_unset=True)
    old_values = {}
    for key, value in update_data.items():
        old_values[key] = getattr(project, key)
        setattr(project, key, value)
    audit = AuditService(db)
    audit.log_change(current_user.id, "project", project.id, "update", old_value=old_values, new_value=update_data)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    audit = AuditService(db)
    audit.log_change(current_user.id, "project", project.id, "delete", old_value={"project_code": project.project_code})
    db.delete(project)
    db.commit()


# ─── Project Members ────────────────────────────────────

@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: str,
    data: ProjectMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    member = ProjectMember(
        project_id=project_id, user_id=data.user_id, assigned_role=data.assigned_role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def list_project_members(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    return members


@router.delete("/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    project_id: str,
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_project_membership(project_id, current_user, db)
    member = db.query(ProjectMember).filter(
        ProjectMember.id == member_id, ProjectMember.project_id == project_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()