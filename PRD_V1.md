# Project Requirement Document (PRD) V1
## Enterprise Project Planning & Scheduling System
## Primavera-like Scheduler / Planner Platform named Qplan

---

# 1. Purpose

Build a multi-user, web-based project planning and scheduling system similar in behavior to Primavera P6 / Microsoft Project named Qplan, focused on professional planning workflows:

- WBS planning
- Activity scheduling
- Dependency logic
- CPM calculation
- Progress update handling
- Baseline control
- Reporting
- Approval workflow
- Audit trail
- Multi-user collaboration

This PRD is written for an AI Agent to implement the application in a controlled, modular, and expandable way.

---

# 2. Product Principles

1. Scheduling logic is the core product.
2. Database design must support real planning workflows.
3. The frontend must never calculate schedule dates.
4. The backend owns schedule logic and validation.
5. The system must work across Windows, Linux, and macOS for development.
6. Supabase is used for Auth, PostgreSQL, and Storage.
7. Codebase must be team-friendly and stored in GitHub.
8. The MVP must be buildable without overengineering.
9. Expandability must be preserved for future features.

---

# 3. Scope

## In Scope for V1

- Supabase Auth
- Supabase PostgreSQL
- Supabase Storage
- React frontend
- FastAPI backend
- WBS
- Activities
- Activity codes
- Dependency logic
- CPM scheduling engine
- Data Date / Status Date
- Baselines
- Reports
- GitHub collaboration
- Docker-based development

## Deferred to Later Versions

- Celery / Redis job queue
- Resource leveling engine
- Portfolio-level optimization
- Advanced risk module
- AI-assisted schedule recommendations
- Mobile app
- Offline mode
- Approval workflow
- Progress updates

---

# 4. Recommended Tech Stack

## Frontend
- React
- TypeScript
- Vite
- Ant Design
- Bryntum Gantt trial for evaluation

## Backend
- FastAPI (Python)

## Database
- Supabase PostgreSQL

## Authentication
- Supabase Auth

## File Storage
- Supabase Storage

## ORM / Database Access
- SQLAlchemy Core for scheduling reads
- SQLAlchemy ORM only for simple CRUD if needed
- Alembic for migrations

## Source Control
- GitHub

## Deployment
- Linux VPS (Alibaba Cloud Simple Application Server preferred)

## Containerization
- Docker
- Docker Compose

---

# 5. Architecture Rules

## 5.1 Supabase Responsibility
Supabase is used for:
- Authentication
- Managed PostgreSQL
- File storage
- User identity foundation

Supabase must not contain the business brain of the scheduling system.

## 5.2 FastAPI Responsibility
FastAPI must own:
- dependency validation
- CPM calculations
- progress-aware schedule recalculation
- baseline comparison logic
- reporting logic
- business rule enforcement
- access control enforcement

## 5.3 Authorization Strategy
Use backend-driven authorization.

Rule:
- do not mix complex authorization logic between RLS and backend business logic for the core product
- backend checks project membership and role on every request
- Supabase Auth only verifies identity
- FastAPI decides access based on project_members and roles

## 5.4 Scheduling Engine Access Pattern
The scheduling engine must not load full ORM objects for CPM computation.

Use:
- raw SQL
- SQLAlchemy Core
- flat dictionaries / dataclasses

Avoid:
- session.query(Activity).all()
- heavy ORM hydration for large schedules

---

# 6. Development Environment Standards

Development must work on:
- Windows
- Linux
- macOS

Production deployment target:
- Linux VPS (Alibaba Cloud Simple Application Server preferred)

## Development Rules
- Docker-first
- path-independent
- OS-agnostic
- reproducible
- no hardcoded local paths
- no OS-specific shell assumptions

## Local Development Services
Use Docker Compose for:
- frontend
- backend
- local PostgreSQL for development
- local testing utilities

Supabase remains the production-grade remote platform for auth, storage, and hosted PostgreSQL.

---

# 7. GitHub Collaboration Standards

## Branching Model
- main â production
- develop â integration / staging
- feature/* â feature work
- hotfix/* â urgent fixes

## Collaboration Rules
- pull request required
- code review required
- no direct push to main
- feature work must be modular
- commit messages must be meaningful

## Environment Files
- .env.example
- .env.local
- .env.production

Never commit secrets.

---

# 8. Core User Roles

- Admin
- Project Manager
- Planner / Scheduler
- Engineer
- Approver
- Viewer

## Access Expectations
- Admin manages system settings
- Planner edits logic and schedule
- Project Manager reviews and approves
- Engineer updates progress
- Approver confirms baselines
- Viewer read-only access

---

# 9. Functional Modules

## 9.1 Authentication & Session
- Supabase Auth login
- session handling
- role binding to application profile
- project access validation

## 9.2 Project Setup
- create project
- project metadata
- project calendar
- project data date
- project settings

## 9.3 WBS Management
- hierarchical WBS structure
- parent-child nodes
- WBS codes
- WBS rollup

## 9.4 Activity Management
- create / edit / delete activities
- activity dates
- durations
- milestones
- status
- owner assignment
- activity code assignment

## 9.5 Dependency Management
Supported logic:
- Finish-to-Start (FS)
- Start-to-Start (SS)
- Finish-to-Finish (FF)
- Start-to-Finish (SF)

Features:
- predecessor / successor mapping
- lag / lead
- circular logic prevention
- dependency validation

## 9.6 Scheduling Engine
- forward pass
- backward pass
- early dates
- late dates
- total float
- free float
- critical path detection
- progress-aware recalculation

## 9.7 Constraints
Supported constraints:
- Must Start On
- Must Finish On
- Start No Earlier Than
- Finish No Later Than

## 9.8 Baseline Management
- create baseline snapshot
- approve baseline
- compare current vs baseline
- maintain baseline relationships

## 9.9 Progress Updates
- actual start
- actual finish
- percent complete
- remaining duration
- progress comments
- status date / data date based update logic

## 9.10 Resources
- resource master
- assignment to activities
- planned hours
- future expansion for resource leveling

## 9.11 Reports & Dashboard
- critical activities
- delay summary
- S-curve
- manpower summary
- schedule variance
- baseline comparison

## 9.12 Audit Trail
- create/update/delete tracking
- before/after values
- user attribution
- timestamp history

## 9.13 Attachments
- store supporting files in Supabase Storage
- link files to project or activity

---

# 10. Database Schema

The schema below is the minimum required for a real planning system.

## 10.1 roles
Fields:
- id UUID PK
- role_name VARCHAR UNIQUE
- created_at TIMESTAMP

## 10.2 users
Fields:
- id UUID PK
- auth_user_id UUID UNIQUE
- full_name VARCHAR
- email VARCHAR UNIQUE
- role_id UUID FK roles.id
- created_at TIMESTAMP
- updated_at TIMESTAMP

Note:
auth_user_id maps the application user profile to Supabase Auth identity.

## 10.3 projects
Fields:
- id UUID PK
- project_code VARCHAR UNIQUE
- project_name VARCHAR
- client_name VARCHAR
- description TEXT
- project_status VARCHAR
- start_date DATE
- finish_date DATE
- data_date DATE
- created_by UUID FK users.id
- created_at TIMESTAMP
- updated_at TIMESTAMP

Important:
data_date is mandatory for CPM and progress-aware logic.

## 10.4 project_members
Fields:
- id UUID PK
- project_id UUID FK projects.id
- user_id UUID FK users.id
- assigned_role VARCHAR
- created_at TIMESTAMP

## 10.5 calendars
Fields:
- id UUID PK
- project_id UUID FK projects.id
- calendar_name VARCHAR
- working_days JSONB
- holidays JSONB
- daily_hours NUMERIC
- created_at TIMESTAMP

## 10.6 wbs
Fields:
- id UUID PK
- project_id UUID FK projects.id
- parent_id UUID FK wbs.id nullable
- wbs_code VARCHAR
- wbs_name VARCHAR
- level INTEGER
- sort_order INTEGER
- created_at TIMESTAMP
- updated_at TIMESTAMP

## 10.7 activities
Fields:
- id UUID PK
- project_id UUID FK projects.id
- wbs_id UUID FK wbs.id
- activity_code VARCHAR
- activity_name VARCHAR
- activity_type VARCHAR
- duration_days NUMERIC
- planned_start DATE nullable
- planned_finish DATE nullable
- actual_start DATE nullable
- actual_finish DATE nullable
- remaining_duration_days NUMERIC nullable
- percent_complete_method VARCHAR
- duration_percent_complete NUMERIC nullable
- physical_percent_complete NUMERIC nullable
- units_percent_complete NUMERIC nullable
- status VARCHAR
- is_milestone BOOLEAN
- owner_id UUID FK users.id nullable
- created_at TIMESTAMP
- updated_at TIMESTAMP

### Important scheduling fields
- percent_complete_method must be explicit
- valid values include:
  - Duration
  - Physical
  - Units
  - LevelOfEffort

## 10.8 activity_relationships
Fields:
- id UUID PK
- predecessor_id UUID FK activities.id
- successor_id UUID FK activities.id
- relationship_type VARCHAR
- lag_days NUMERIC
- created_at TIMESTAMP

Allowed relationship types:
- FS
- SS
- FF
- SF

## 10.9 activity_constraints
Fields:
- id UUID PK
- activity_id UUID FK activities.id
- constraint_type VARCHAR
- constraint_date DATE
- created_at TIMESTAMP

## 10.10 activity_codes
Fields:
- id UUID PK
- project_id UUID FK projects.id nullable
- code_type VARCHAR
- code_value VARCHAR
- code_description VARCHAR
- created_at TIMESTAMP

Notes:
- code_type examples: Phase, Discipline, Area, Responsible Engineer, System
- codes are separate from WBS

## 10.11 activity_code_assignments
Fields:
- id UUID PK
- activity_id UUID FK activities.id
- activity_code_id UUID FK activity_codes.id
- created_at TIMESTAMP

One activity may have many activity codes.

## 10.12 baselines
Fields:
- id UUID PK
- project_id UUID FK projects.id
- baseline_name VARCHAR
- revision_no INTEGER
- baseline_type VARCHAR
- approved_by UUID FK users.id nullable
- approved_at TIMESTAMP nullable
- created_at TIMESTAMP

## 10.13 baseline_activities
Fields:
- id UUID PK
- baseline_id UUID FK baselines.id
- activity_id UUID FK activities.id
- baseline_start DATE
- baseline_finish DATE
- baseline_duration NUMERIC
- baseline_percent_complete_method VARCHAR
- created_at TIMESTAMP

## 10.14 baseline_relationships
Fields:
- id UUID PK
- baseline_id UUID FK baselines.id
- predecessor_activity_id UUID FK activities.id
- successor_activity_id UUID FK activities.id
- relationship_type VARCHAR
- lag_days NUMERIC
- created_at TIMESTAMP

This table is mandatory for forensic delay analysis.

## 10.15 progress_updates
Fields:
- id UUID PK
- activity_id UUID FK activities.id
- data_date DATE
- actual_start DATE nullable
- actual_finish DATE nullable
- remaining_duration_days NUMERIC nullable
- duration_percent_complete NUMERIC nullable
- physical_percent_complete NUMERIC nullable
- units_percent_complete NUMERIC nullable
- remarks TEXT
- updated_by UUID FK users.id
- created_at TIMESTAMP

## 10.16 resources
Fields:
- id UUID PK
- project_id UUID FK projects.id nullable
- resource_name VARCHAR
- resource_type VARCHAR
- unit VARCHAR
- created_at TIMESTAMP

## 10.17 resource_assignments
Fields:
- id UUID PK
- activity_id UUID FK activities.id
- resource_id UUID FK resources.id
- quantity NUMERIC
- planned_hours NUMERIC
- created_at TIMESTAMP

## 10.18 approvals
Fields:
- id UUID PK
- project_id UUID FK projects.id
- approval_type VARCHAR
- approval_status VARCHAR
- approved_by UUID FK users.id nullable
- approval_date TIMESTAMP nullable
- remarks TEXT nullable

## 10.19 audit_logs
Fields:
- id UUID PK
- user_id UUID FK users.id
- entity_name VARCHAR
- entity_id UUID
- action_type VARCHAR
- old_value JSONB
- new_value JSONB
- created_at TIMESTAMP

## 10.20 attachments
Fields:
- id UUID PK
- project_id UUID FK projects.id nullable
- activity_id UUID FK activities.id nullable
- file_name VARCHAR
- file_path VARCHAR
- file_size NUMERIC nullable
- uploaded_by UUID FK users.id
- created_at TIMESTAMP

---

# 11. ERD Logic

## Core Relationship Map

```text
Project
 âââ Calendar
 âââ Project Members
 âââ WBS
 â    âââ Activities
 â         âââ Activity Relationships
 â         âââ Activity Constraints
 â         âââ Activity Codes
 â         âââ Progress Updates
 â         âââ Resource Assignments
 â         âââ Baseline Snapshots
 âââ Baselines
 â    âââ Baseline Activities
 â    âââ Baseline Relationships
 âââ Approvals
 âââ Attachments
 âââ Audit Logs
```

## ERD Rules
- each activity belongs to exactly one WBS node
- each activity may have many dependencies
- each activity may have many activity codes
- each activity may have many progress updates
- each baseline must snapshot both activity values and relationships
- project-level security is enforced through project_members

---

# 12. Scheduling Logic

## 12.1 Dependency Types
The engine must support:

- FS = Finish-to-Start
- SS = Start-to-Start
- FF = Finish-to-Finish
- SF = Start-to-Finish

## 12.2 Date Calculation Rules
The backend must calculate:

- early start
- early finish
- late start
- late finish
- total float
- free float
- critical path

## 12.3 Data Date Rule
The data_date is the current status date used by the scheduler.

The system must recalculate all incomplete work relative to the data date.

## 12.4 Actuals Rule
Actual dates always override calculated dates where applicable.

If an activity is complete:
- actual_finish governs the activity completion
- remaining duration becomes zero

If an activity is in progress:
- actual_start must be respected
- remaining duration must be tracked
- the schedule engine must determine forward movement from data date

## 12.5 Percent Complete Rule
The system must explicitly know the progress method.

Required supported methods:
- Duration
- Physical
- Units
- LevelOfEffort

Rules:
- duration_percent_complete affects duration-based progress
- physical_percent_complete affects physically measured progress
- units_percent_complete affects resource-based progress
- LOE activities follow their own logic and do not drive critical path in the same way as normal activities

## 12.6 Scheduling Mode Rule
Do not implement a vague "manual scheduling" mode that bypasses CPM logic.

Instead:
- allow actual dates entry
- allow constraints
- allow controlled drag/drop that converts to valid schedule edits
- never allow UI actions to silently corrupt the logic network

## 12.7 Out-of-Sequence Progress
The engine must be able to handle incomplete work when the data date passes beyond the original logic.

The engine must clearly define whether the project uses:
- retained logic
- progress override
- actual dates respected first

For V1, define the default behavior as:
- actual dates are preserved
- incomplete work is recalculated from the data date
- logic violations must be surfaced, not hidden

## 12.8 Validation Rules
The scheduler must reject:
- circular dependencies
- impossible constraints
- invalid lag combinations
- orphaned activities with broken references
- dependencies that violate project rules

---

# 13. Scheduling API Contract

## Endpoint
`POST /api/projects/{project_id}/schedule`

## Purpose
Recalculate the schedule for a project using current activity data, dependencies, constraints, and data date.

## Request Body
```json
{
  "data_date": "2026-04-21",
  "mode": "recalculate",
  "ignore_actuals_before": "2026-04-20"
}
```

## Response Body
```json
{
  "project_id": "uuid",
  "data_date": "2026-04-21",
  "activities": [
    {
      "activity_id": "uuid",
      "early_start": "2026-04-21",
      "early_finish": "2026-04-23",
      "late_start": "2026-04-22",
      "late_finish": "2026-04-24",
      "total_float": 2,
      "free_float": 1,
      "is_critical": false,
      "status": "in_progress"
    }
  ],
  "critical_path": ["uuid", "uuid", "uuid"],
  "warnings": []
}
```

## Rule
Frontend must never compute schedule dates locally.
Frontend only sends the request and renders returned results.

---

# 14. Workflow Flows

## 14.1 Project Planning Flow
```text
Create Project
â
Set Data Date
â
Create Calendar
â
Build WBS
â
Create Activities
â
Assign Activity Codes
â
Add Dependencies
â
Apply Constraints
â
Run CPM Schedule
â
Review Critical Path
â
Create Baseline
â
Approve Baseline
â
Track Progress
â
Recalculate Schedule
```

## 14.2 Baseline Flow
```text
Create Baseline
â
Snapshot Activities
â
Snapshot Relationships
â
Submit Approval
â
Approve or Reject
â
Freeze Baseline
```

## 14.3 Progress Update Flow
```text
Submit Progress
â
Validate Actual Dates / Remaining Duration
â
Recalculate Schedule using Data Date
â
Compare to Baseline
â
Show Variance
â
Log Audit Trail
```

## 14.4 Dependency Change Flow
```text
Change Relationship
â
Validate Link
â
Check Circular Dependency
â
Recalculate CPM
â
Refresh Gantt
â
Store Revision
```

---

# 15. UI Screen Architecture

## Main Navigation
```text
Login
â
Dashboard
â
Project Workspace
 âââ Project Settings
 âââ WBS
 âââ Activities
 âââ Gantt Chart
 âââ Relationships
 âââ Constraints
 âââ Activity Codes
 âââ Resources
 âââ Baselines
 âââ Progress Updates
 âââ Reports
 âââ Approvals
 âââ Audit Logs
```

## Screen Requirements

### Login Page
- Supabase Auth login
- session restoration

### Dashboard
- active projects
- critical path alerts
- overdue activities
- baseline status
- recent updates

### Project Workspace
Main working area for planners.

### Gantt View
- interactive schedule chart
- dependency visualization
- critical path highlighting
- drag/drop actions only if they produce valid logic

### Activity Details Drawer / Modal
- dates
- duration
- percent complete
- actuals
- dependencies
- codes
- resources
- audit history

### Baseline Comparison Page
- current vs baseline dates
- variance display
- relationship comparison

### Approval Center
- pending approvals
- approve / reject
- remarks

### Reports Page
- S-curve
- delay report
- manpower histogram
- critical activities
- schedule variance

---

# 16. Non-Functional Requirements

## Performance
The system must support:
- approximately 100 users
- large schedules
- complex dependency networks

## Reliability
- audit logging
- backup strategy
- repeatable schedule calculations

## Security
- Supabase Auth
- backend authorization checks
- secure file access
- role-based permissions

## Maintainability
- modular codebase
- clear service boundaries
- reproducible environments

## Expandability
- future resource leveling
- future AI features
- future portfolio management

---

# 17. MVP Acceptance Criteria

The MVP is complete only when all of the following are true:

- users authenticate via Supabase Auth
- user role is mapped into the app profile
- projects can be created
- data date is supported
- WBS hierarchy works
- activities can be created and edited
- activity codes can be assigned
- all four dependency types work
- CPM schedule calculation is correct
- critical path is generated
- baseline snapshots include both activities and relationships
- progress updates trigger schedule recalculation
- activity percent complete method is explicit
- reports can be viewed
- files can be uploaded to Supabase Storage
- audit logs are stored
- the app can be developed on Windows, Linux, and macOS
- the app can be deployed on a Linux VPS
- the codebase can be managed collaboratively on GitHub

---

# 18. Mandatory Unit Test Scenarios

## Test Case 1: Basic FS Logic
Input:
- Activity A = 3 days
- Activity B = 2 days
- B is FS successor of A
- Data Date = Day 6
- A = 100%
- B = 0%

Expected:
- B starts Day 6
- B finishes Day 7

## Test Case 2: Baseline Relationship Preservation
Input:
- Baseline has A -> B
- Current schedule has A -> C -> B

Expected:
- baseline_relationships preserves original logic
- delay analysis identifies logic change

## Test Case 3: Data Date Progress Behavior
Input:
- Data Date passed original finish date
- activity incomplete
- actual start exists
- remaining duration exists

Expected:
- schedule recalculates from data date
- incomplete work does not vanish
- logic violations are visible

## Test Case 4: Activity Code Filtering
Input:
- multiple activity codes assigned to one activity

Expected:
- activity can be filtered by any assigned code
- WBS remains unchanged

---

# 19. Implementation Guidance for the AI Agent

The agent must:
- implement schema first
- implement auth and project membership next
- implement activity and WBS CRUD next
- implement scheduling engine after data model is stable
- implement baseline snapshotting before advanced reporting
- implement frontend Gantt only after API contract exists
- avoid premature optimization
- keep the product modular

The agent must not:
- use SQLite for production
- build scheduling in the frontend
- hide schedule logic behind vague flags
- omit baseline relationships
- omit data date
- mix authorization approaches without a rule

---

# 20. Final Note

This system is not a generic CRUD app.

It is a schedule engine with a UI.

If the schedule logic is correct, the rest becomes manageable.
If the schedule logic is wrong, the entire product fails.

---

# End of PRD V1
