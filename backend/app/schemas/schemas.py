"""Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


# ─── Auth ───────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional["UserResponse"] = None


# ─── Role ───────────────────────────────────────────────
class RoleCreate(BaseModel):
    role_name: str


class RoleResponse(BaseModel):
    id: str
    role_name: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── User ───────────────────────────────────────────────
class UserCreate(BaseModel):
    auth_user_id: str
    full_name: Optional[str] = None
    email: str
    role_id: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    auth_user_id: str
    full_name: Optional[str] = None
    email: str
    role_id: Optional[str] = None
    role: Optional[RoleResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Project ────────────────────────────────────────────
class ProjectCreate(BaseModel):
    project_code: str
    project_name: str
    client_name: Optional[str] = None
    description: Optional[str] = None
    project_status: Optional[str] = "planning"
    start_date: Optional[date] = None
    finish_date: Optional[date] = None
    data_date: date


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None
    project_status: Optional[str] = None
    start_date: Optional[date] = None
    finish_date: Optional[date] = None
    data_date: Optional[date] = None


class ProjectResponse(BaseModel):
    id: str
    project_code: str
    project_name: str
    client_name: Optional[str] = None
    description: Optional[str] = None
    project_status: Optional[str] = None
    start_date: Optional[date] = None
    finish_date: Optional[date] = None
    data_date: date
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Project Member ─────────────────────────────────────
class ProjectMemberCreate(BaseModel):
    user_id: str
    assigned_role: str


class ProjectMemberResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    assigned_role: str
    user: Optional[UserResponse] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Calendar ───────────────────────────────────────────
class CalendarCreate(BaseModel):
    calendar_name: str
    working_days: Optional[List[int]] = Field(default=[1, 2, 3, 4, 5])  # Mon=1 to Sun=7
    holidays: Optional[List[str]] = Field(default_factory=list)
    daily_hours: Optional[Decimal] = Decimal("8.0")


class CalendarResponse(BaseModel):
    id: str
    project_id: str
    calendar_name: str
    working_days: Optional[list] = None
    holidays: Optional[list] = None
    daily_hours: Optional[Decimal] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── WBS ────────────────────────────────────────────────
class WBSCreate(BaseModel):
    parent_id: Optional[str] = None
    wbs_code: str
    wbs_name: str
    level: Optional[int] = 0
    sort_order: Optional[int] = 0


class WBSUpdate(BaseModel):
    wbs_code: Optional[str] = None
    wbs_name: Optional[str] = None
    sort_order: Optional[int] = None


class WBSResponse(BaseModel):
    id: str
    project_id: str
    parent_id: Optional[str] = None
    wbs_code: str
    wbs_name: str
    level: Optional[int] = 0
    sort_order: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    children: Optional[List["WBSResponse"]] = None

    model_config = {"from_attributes": True}


# ─── Activity ───────────────────────────────────────────
class ActivityCreate(BaseModel):
    wbs_id: str
    activity_code: str
    activity_name: str
    activity_type: Optional[str] = "task"
    duration_days: Optional[Decimal] = 0
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    remaining_duration_days: Optional[Decimal] = None
    percent_complete_method: Optional[str] = "Duration"
    duration_percent_complete: Optional[Decimal] = 0
    physical_percent_complete: Optional[Decimal] = 0
    units_percent_complete: Optional[Decimal] = 0
    status: Optional[str] = "not_started"
    is_milestone: Optional[bool] = False
    owner_id: Optional[str] = None


class ActivityUpdate(BaseModel):
    wbs_id: Optional[str] = None
    activity_code: Optional[str] = None
    activity_name: Optional[str] = None
    activity_type: Optional[str] = None
    duration_days: Optional[Decimal] = None
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    remaining_duration_days: Optional[Decimal] = None
    percent_complete_method: Optional[str] = None
    duration_percent_complete: Optional[Decimal] = None
    physical_percent_complete: Optional[Decimal] = None
    units_percent_complete: Optional[Decimal] = None
    status: Optional[str] = None
    is_milestone: Optional[bool] = None
    owner_id: Optional[str] = None


class ActivityResponse(BaseModel):
    id: str
    project_id: str
    wbs_id: str
    activity_code: str
    activity_name: str
    activity_type: Optional[str] = None
    duration_days: Optional[Decimal] = 0
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    remaining_duration_days: Optional[Decimal] = None
    percent_complete_method: Optional[str] = "Duration"
    duration_percent_complete: Optional[Decimal] = 0
    physical_percent_complete: Optional[Decimal] = 0
    units_percent_complete: Optional[Decimal] = 0
    status: Optional[str] = "not_started"
    is_milestone: Optional[bool] = False
    owner_id: Optional[str] = None
    # CPM fields
    early_start: Optional[date] = None
    early_finish: Optional[date] = None
    late_start: Optional[date] = None
    late_finish: Optional[date] = None
    total_float: Optional[Decimal] = None
    free_float: Optional[Decimal] = None
    is_critical: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Activity Relationship ──────────────────────────────
class ActivityRelationshipCreate(BaseModel):
    predecessor_id: str
    successor_id: str
    relationship_type: str = "FS"  # FS, SS, FF, SF
    lag_days: Optional[Decimal] = 0


class ActivityRelationshipResponse(BaseModel):
    id: str
    predecessor_id: str
    successor_id: str
    relationship_type: str
    lag_days: Optional[Decimal] = 0
    created_at: Optional[datetime] = None
    predecessor: Optional[ActivityResponse] = None
    successor: Optional[ActivityResponse] = None

    model_config = {"from_attributes": True}


# ─── Activity Constraint ────────────────────────────────
class ActivityConstraintCreate(BaseModel):
    constraint_type: str  # must_start_on, must_finish_on, start_no_earlier_than, finish_no_later_than
    constraint_date: date


class ActivityConstraintResponse(BaseModel):
    id: str
    activity_id: str
    constraint_type: str
    constraint_date: date
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Activity Code ──────────────────────────────────────
class ActivityCodeCreate(BaseModel):
    code_type: str
    code_value: str
    code_description: Optional[str] = None


class ActivityCodeResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    code_type: str
    code_value: str
    code_description: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Activity Code Assignment ───────────────────────────
class ActivityCodeAssignmentCreate(BaseModel):
    activity_code_id: str


class ActivityCodeAssignmentResponse(BaseModel):
    id: str
    activity_id: str
    activity_code_id: str
    activity_code: Optional[ActivityCodeResponse] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Baseline ───────────────────────────────────────────
class BaselineCreate(BaseModel):
    baseline_name: str
    baseline_type: Optional[str] = "project"


class BaselineResponse(BaseModel):
    id: str
    project_id: str
    baseline_name: str
    revision_no: Optional[int] = 1
    baseline_type: Optional[str] = "project"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BaselineActivityResponse(BaseModel):
    id: str
    baseline_id: str
    activity_id: str
    baseline_start: date
    baseline_finish: date
    baseline_duration: Decimal
    baseline_percent_complete_method: Optional[str] = "Duration"
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BaselineRelationshipResponse(BaseModel):
    id: str
    baseline_id: str
    predecessor_activity_id: str
    successor_activity_id: str
    relationship_type: str
    lag_days: Optional[Decimal] = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Progress Update ────────────────────────────────────
class ProgressUpdateCreate(BaseModel):
    data_date: date
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    remaining_duration_days: Optional[Decimal] = None
    duration_percent_complete: Optional[Decimal] = None
    physical_percent_complete: Optional[Decimal] = None
    units_percent_complete: Optional[Decimal] = None
    remarks: Optional[str] = None


class ProgressUpdateResponse(BaseModel):
    id: str
    activity_id: str
    data_date: date
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    remaining_duration_days: Optional[Decimal] = None
    duration_percent_complete: Optional[Decimal] = None
    physical_percent_complete: Optional[Decimal] = None
    units_percent_complete: Optional[Decimal] = None
    remarks: Optional[str] = None
    updated_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Resource ───────────────────────────────────────────
class ResourceCreate(BaseModel):
    resource_name: str
    resource_type: Optional[str] = None
    unit: Optional[str] = None


class ResourceResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    resource_name: str
    resource_type: Optional[str] = None
    unit: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ResourceAssignmentCreate(BaseModel):
    resource_id: str
    quantity: Optional[Decimal] = 0
    planned_hours: Optional[Decimal] = 0


class ResourceAssignmentResponse(BaseModel):
    id: str
    activity_id: str
    resource_id: str
    quantity: Optional[Decimal] = 0
    planned_hours: Optional[Decimal] = 0
    resource: Optional[ResourceResponse] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Approval ───────────────────────────────────────────
class ApprovalCreate(BaseModel):
    approval_type: str
    remarks: Optional[str] = None


class ApprovalUpdate(BaseModel):
    approval_status: str  # approved, rejected
    remarks: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: str
    project_id: str
    approval_type: str
    approval_status: Optional[str] = "pending"
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    remarks: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Audit Log ──────────────────────────────────────────
class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    entity_name: str
    entity_id: str
    action_type: str
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Attachment ─────────────────────────────────────────
class AttachmentResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    activity_id: Optional[str] = None
    file_name: str
    file_path: str
    file_size: Optional[Decimal] = None
    uploaded_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Scheduling ─────────────────────────────────────────
class ScheduleRequest(BaseModel):
    data_date: date
    mode: Optional[str] = "recalculate"
    ignore_actuals_before: Optional[date] = None


class ScheduleActivityResult(BaseModel):
    activity_id: str
    early_start: Optional[date] = None
    early_finish: Optional[date] = None
    late_start: Optional[date] = None
    late_finish: Optional[date] = None
    total_float: Optional[Decimal] = None
    free_float: Optional[Decimal] = None
    is_critical: Optional[bool] = False
    status: Optional[str] = None


class ScheduleResponse(BaseModel):
    project_id: str
    data_date: date
    activities: List[ScheduleActivityResult]
    critical_path: List[str]
    warnings: List[str]


# ─── Reports ────────────────────────────────────────────
class CriticalActivityReport(BaseModel):
    activity_id: str
    activity_code: str
    activity_name: str
    early_start: Optional[date] = None
    early_finish: Optional[date] = None
    total_float: Optional[Decimal] = None
    status: Optional[str] = None


class ScheduleVarianceReport(BaseModel):
    activity_id: str
    activity_code: str
    activity_name: str
    current_start: Optional[date] = None
    current_finish: Optional[date] = None
    baseline_start: Optional[date] = None
    baseline_finish: Optional[date] = None
    start_variance_days: Optional[Decimal] = None
    finish_variance_days: Optional[Decimal] = None


class DashboardResponse(BaseModel):
    total_projects: int
    active_projects: int
    critical_activities: int
    overdue_activities: int
    pending_approvals: int
    recent_updates: List[dict]