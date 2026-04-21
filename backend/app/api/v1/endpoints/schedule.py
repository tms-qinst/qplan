"""Schedule endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user, check_project_membership
from app.models.user import User
from app.services.schedule_service import ScheduleService
from app.schemas.schemas import ScheduleRequest, ScheduleResponse

router = APIRouter(prefix="/projects/{project_id}", tags=["Schedule"])


@router.post("/schedule", response_model=ScheduleResponse)
def run_schedule(
    project_id: str,
    data: ScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run CPM schedule calculation for a project.

    Frontend must never compute schedule dates locally.
    Frontend only sends the request and renders returned results.
    """
    check_project_membership(project_id, current_user, db)
    service = ScheduleService(db)
    result = service.run_schedule(
        project_id=project_id,
        data_date=data.data_date,
        mode=data.mode,
        ignore_actuals_before=data.ignore_actuals_before,
    )
    return result