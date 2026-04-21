# Qplan �?Enterprise Project Planning & Scheduling System

A Primavera P6-like web-based project planning and scheduling platform. Qplan provides professional-grade CPM scheduling, WBS management, dependency logic, baseline control, and reporting �?all in a modern web interface.

---

## Table of Contents

- [Qplan �?Enterprise Project Planning \& Scheduling System](#qplan--enterprise-project-planning--scheduling-system)
  - [Table of Contents](#table-of-contents)
  - [Architecture Overview](#architecture-overview)
    - [Key Architecture Rules](#key-architecture-rules)
  - [Tech Stack](#tech-stack)
  - [Prerequisites](#prerequisites)
    - [For Users (Running the App)](#for-users-running-the-app)
    - [For Developers](#for-developers)
  - [Quick Start (Docker)](#quick-start-docker)
  - [Local Development Setup](#local-development-setup)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
    - [Production Build](#production-build)
  - [Environment Variables Reference](#environment-variables-reference)
    - [Backend (`backend/.env`)](#backend-backendenv)
    - [Frontend (`frontend/.env`)](#frontend-frontendenv)
  - [Database Setup \& Migrations](#database-setup--migrations)
    - [Initial Setup](#initial-setup)
    - [Creating a New Migration](#creating-a-new-migration)
    - [Migration Commands](#migration-commands)
    - [Database Schema](#database-schema)
  - [Running Tests](#running-tests)
    - [Backend Tests (CPM Engine)](#backend-tests-cpm-engine)
    - [Frontend Build Check](#frontend-build-check)
  - [User Guide](#user-guide)
    - [1. Logging In](#1-logging-in)
    - [2. Dashboard](#2-dashboard)
    - [3. Creating a Project](#3-creating-a-project)
    - [4. Project Workspace](#4-project-workspace)
    - [5. Building the WBS](#5-building-the-wbs)
    - [6. Creating Activities](#6-creating-activities)
    - [7. Adding Dependencies](#7-adding-dependencies)
    - [8. Running the Schedule (CPM)](#8-running-the-schedule-cpm)
    - [9. Reviewing the Gantt Chart](#9-reviewing-the-gantt-chart)
    - [10. Creating Baselines](#10-creating-baselines)
    - [11. Reports](#11-reports)
  - [Developer Guide](#developer-guide)
    - [Project Structure](#project-structure)
    - [Adding a New API Endpoint](#adding-a-new-api-endpoint)
    - [Adding a New Database Model](#adding-a-new-database-model)
    - [Adding a New Frontend Page](#adding-a-new-frontend-page)
    - [Code Style \& Conventions](#code-style--conventions)
  - [Deployment](#deployment)
    - [Production Deployment on Linux VPS](#production-deployment-on-linux-vps)
    - [Production Checklist](#production-checklist)
  - [API Reference](#api-reference)
    - [Authentication](#authentication)
    - [Projects](#projects)
    - [WBS](#wbs)
    - [Activities](#activities)
    - [Relationships](#relationships)
    - [Schedule](#schedule)
    - [Baselines](#baselines)
  - [Troubleshooting](#troubleshooting)
    - [Frontend won't start](#frontend-wont-start)
    - [Backend database connection fails](#backend-database-connection-fails)
    - [Docker issues](#docker-issues)
    - [Migration errors](#migration-errors)
  - [Branching \& Collaboration](#branching--collaboration)
    - [Branch Model](#branch-model)
    - [Workflow](#workflow)
    - [Rules](#rules)
  - [License](#license)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────�?
�?                   Browser (React SPA)                    �?
�? Login · Dashboard · WBS · Activities · Gantt · Reports  �?
└──────────────┬─────────────────────────┬─────────────────�?
               �?                        �?
     Supabase Auth                FastAPI Backend
     (JWT tokens)                 (Port 8000)
               �?                        �?
               �?             ┌──────────┴──────────�?
               �?             �? Scheduling Engine   �?
               �?             �? CPM · Float · Path  �?
               �?             └──────────┬──────────�?
               �?                        �?
       ┌───────┴─────────────────────────┴───────�?
       �?           Supabase PostgreSQL           �?
       �?  (Auth DB + App Data + Storage)         �?
       └──────────────────────────────────────────�?
```

### Key Architecture Rules
- **Frontend never computes schedule dates** �?all CPM logic runs server-side
- **Backend owns business logic** �?dependency validation, CPM calculations, authorization
- **Supabase handles identity** �?authentication only; FastAPI enforces authorization
- **Scheduling engine uses flat dictionaries** �?no heavy ORM hydration for CPM computation

---

## Tech Stack

| Layer       | Technology                         | Version     |
|-------------|------------------------------------|-------------|
| Frontend    | React + TypeScript + Vite          | React 18, Vite 6 |
| UI Library  | Ant Design                         | 5.x         |
| Routing     | React Router DOM                   | 6.x         |
| Backend     | FastAPI (Python)                   | 3.12+       |
| ORM         | SQLAlchemy + Alembic               | 2.0.x       |
| Database    | PostgreSQL (via Supabase)          | 16          |
| Auth        | Supabase Auth                      | �?          |
| Storage     | Supabase Storage                   | �?          |
| HTTP Client | Axios (frontend) / httpx (backend) | �?          |
| Container   | Docker + Docker Compose            | �?          |

---

## Prerequisites

### For Users (Running the App)
- A modern web browser (Chrome, Firefox, Edge, Safari)
- A Qplan account (created by your administrator)

### For Developers
- **Python 3.12+** �?[python.org](https://python.org)
- **Node.js 20+** �?[nodejs.org](https://nodejs.org)
- **Git** �?[git-scm.com](https://git-scm.com)
- **Docker & Docker Compose** (optional, for containerized setup) �?[docker.com](https://docker.com)

---

## Quick Start (Docker)

The fastest way to get Qplan running using Docker:

```bash
# 1. Clone the repository
git clone https://github.com/tms-qinst/qplan.git
cd qplan

# 2. Start all services (backend + frontend)
docker-compose up --build

# 3. Open your browser
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

To also run a local PostgreSQL (optional, Supabase is the default):

```bash
docker-compose --profile local-db up --build
```

To stop:

```bash
docker-compose down
```

---

## Local Development Setup

Use this method if you want to develop without Docker.

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create a Python virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Create your .env file from the example
# (Already configured with Supabase credentials)
# Edit if needed �?see Environment Variables Reference below

# 6. Run database migrations
alembic upgrade head

# 7. Start the backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at **http://localhost:8000**

API documentation (Swagger UI): **http://localhost:8000/docs**

### Frontend Setup

```bash
# 1. Open a new terminal and navigate to the frontend directory
cd frontend

# 2. Install Node.js dependencies
npm install

# 3. Create your .env file from the example
# (Already configured with Supabase credentials)
# Edit if needed �?see Environment Variables Reference below

# 4. Start the development server
npm run dev
```

The frontend will be available at **http://localhost:5173**

### Production Build

```bash
cd frontend
npm run build        # TypeScript check + Vite production build
npm run preview      # Preview the production build locally
```

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://ulvsophbtfdhfoypyqts.supabase.co` |
| `SUPABASE_KEY` | Supabase publishable key | `sb_publishable_j-7Zl...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (admin) | (leave blank for dev) |
| `DATABASE_URL` | PostgreSQL connection (sync) | `postgresql+psycopg2://postgres:...` |
| `DATABASE_URL_ASYNC` | PostgreSQL connection (async) | `postgresql+asyncpg://postgres:...` |
| `JWT_SECRET` | JWT signing secret | `change-me-in-production` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173,http://localhost:3000` |
| `DEBUG` | Enable debug mode | `true` / `false` |
| `SUPABASE_STORAGE_BUCKET` | File storage bucket name | `attachments` |

### Frontend (`frontend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_SUPABASE_URL` | Supabase project URL | `https://ulvsophbtfdhfoypyqts.supabase.co` |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Supabase publishable key | `sb_publishable_j-7Zl...` |
| `VITE_API_URL` | Backend API base URL | `/api/v1` |

---

## Database Setup & Migrations

Qplan uses **Alembic** for database schema migrations, backed by **Supabase PostgreSQL**.

### Initial Setup

```bash
cd backend

# Ensure your virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run all pending migrations
alembic upgrade head
```

### Creating a New Migration

```bash
# After modifying SQLAlchemy models in backend/app/models/

# Auto-generate a migration (detects model changes)
alembic revision --autogenerate -m "add_new_table"

# Or create an empty migration manually
alembic revision -m "custom_migration"
```

### Migration Commands

```bash
alembic current          # Show current migration version
alembic history          # Show migration history
alembic upgrade head     # Apply all pending migrations
alembic downgrade -1     # Roll back one migration
alembic upgrade +1       # Apply next migration
```

### Database Schema

The application uses **20 tables** covering the full planning lifecycle:

```
roles �?users �?project_members �?projects
                        �?
              calendars · wbs �?activities
                                  �?
              activity_relationships · activity_constraints
              activity_codes �?activity_code_assignments
              progress_updates · resource_assignments �?resources
              baselines �?baseline_activities · baseline_relationships
              approvals · audit_logs · attachments
```

---

## Running Tests

### Backend Tests (CPM Engine)

```bash
cd backend
pytest tests/test_cpm.py -v
```

Test cases include:
- **Basic FS logic** �?Activity A (3 days) �?Activity B (2 days) with 100% progress
- **SS relationship** �?Start-to-Start with lag
- **Circular dependency detection** �?A �?B �?C �?A must be rejected
- **Critical path identification** �?Longest path through the network

### Frontend Build Check

```bash
cd frontend
npm run build    # TypeScript compilation + Vite build
```

---

## User Guide

### 1. Logging In

1. Open your browser and navigate to the Qplan URL (e.g., `http://localhost:5173`)
2. Enter your **email** and **password**
3. Click **Sign In**
4. Authentication is handled by Supabase Auth
5. If you don't have an account, contact your system administrator

### 2. Dashboard

After logging in, you'll see the **Dashboard** with:

- **Active Projects** �?List of projects you're a member of
- **Critical Path Alerts** �?Activities that are behind schedule
- **Overdue Activities** �?Activities past their planned finish date
- **Baseline Status** �?Which projects have approved baselines
- **Recent Updates** �?Latest progress updates across your projects

Click any project card to enter its workspace.

### 3. Creating a Project

1. From the Dashboard, click **"New Project"**
2. Fill in the project details:
   - **Project Code** �?Unique identifier (e.g., `PRJ-001`)
   - **Project Name** �?Descriptive name
   - **Client Name** �?Client or stakeholder
   - **Description** �?Project scope description
   - **Start Date** �?Planned project start
   - **Data Date** �?Current status date (critical for CPM)
3. Click **Create**
4. You will be automatically added as the Project Manager

### 4. Project Workspace

The Project Workspace is your main planning area. Use the **sidebar navigation** to access:

| Tab | Purpose |
|-----|---------|
| **Activities** | Create, edit, delete activities |
| **WBS** | Manage the Work Breakdown Structure |
| **Schedule** | Run CPM calculations and view results |
| **Baselines** | Create and compare baseline snapshots |
| **Relationships** | Manage dependency links |
| **Reports** | View schedule analytics |

### 5. Building the WBS

The **Work Breakdown Structure (WBS)** organizes your project into hierarchical phases:

1. Go to the **WBS** tab in your project workspace
2. Click **"Add WBS Node"** to create a top-level element
3. Enter the **WBS Code** (e.g., `1.0`) and **WBS Name** (e.g., `Engineering`)
4. To create sub-elements, select a parent WBS node and click **"Add Child"**
5. Continue building the hierarchy:
   ```
   1.0 Engineering
     1.1 Civil Works
     1.2 Mechanical
     1.3 Electrical
   2.0 Procurement
     2.1 Materials
     2.2 Equipment
   3.0 Construction
   ```

### 6. Creating Activities

1. Go to the **Activities** tab
2. Click **"New Activity"**
3. Fill in the activity details:

   | Field | Description |
   |-------|-------------|
   | **Activity Code** | Unique ID (e.g., `A1010`) |
   | **Activity Name** | Description of work |
   | **WBS** | Assign to a WBS node |
   | **Type** | Task Dependent / Milestone |
   | **Duration (days)** | Planned duration |
   | **Percent Complete Method** | Duration / Physical / Units |
   | **Owner** | Responsible person |

4. Click **Save**
5. Repeat for all activities in your project

### 7. Adding Dependencies

Dependencies define the logic between activities. Qplan supports four relationship types:

| Type | Code | Meaning |
|------|------|---------|
| Finish-to-Start | **FS** | Predecessor must finish before successor starts |
| Start-to-Start | **SS** | Both activities start together |
| Finish-to-Finish | **FF** | Both activities finish together |
| Start-to-Finish | **SF** | Successor finishes when predecessor starts |

To add a dependency:
1. In the **Activities** table, select an activity
2. Open the **Relationships** section
3. Click **"Add Dependency"**
4. Select the **Predecessor** activity
5. Choose the **Relationship Type** (FS, SS, FF, SF)
6. Enter **Lag days** if needed (positive = delay, negative = overlap)
7. Click **Save**

> ⚠️ **Circular dependencies are automatically detected and rejected.**

### 8. Running the Schedule (CPM)

The CPM (Critical Path Method) engine calculates all schedule dates:

1. Go to the **Schedule** tab in your project workspace
2. Verify the **Data Date** (the status date for calculations)
3. Click **"Run Schedule"**
4. The engine performs:
   - **Forward Pass** �?Calculates Early Start (ES) and Early Finish (EF)
   - **Backward Pass** �?Calculates Late Start (LS) and Late Finish (LF)
   - **Float Calculation** �?Total Float and Free Float for each activity
   - **Critical Path Detection** �?Activities with zero total float
5. Review results in the table:
   - Activities highlighted in **red** are on the critical path
   - **Warnings** (if any) are displayed at the top

> 📌 **Important:** The frontend never calculates dates locally. All CPM logic runs on the FastAPI backend.

### 9. Reviewing the Gantt Chart

1. After running the schedule, go to the **Gantt** view
2. The timeline displays:
   - **Blue bars** �?Normal activities
   - **Red bars** �?Critical path activities
   - **Diamond markers** �?Milestones
   - **Arrows** �?Dependency relationships
3. Drag/drop actions are supported but must produce valid logic
4. Hover over any bar to see detailed dates and float

### 10. Creating Baselines

A baseline is a snapshot of the approved schedule:

1. Go to the **Baselines** tab
2. Click **"Create Baseline"**
3. Enter a **Baseline Name** and **Revision Number**
4. Click **Create** �?this snapshots:
   - All activity dates and durations
   - All dependency relationships
5. To compare current schedule vs baseline:
   - Select a baseline and click **"Compare"**
   - Variance is displayed for each activity:
     - Start variance (days)
     - Finish variance (days)
     - Duration variance (days)

> Baselines capture both activities AND relationships for forensic delay analysis.

### 11. Reports

The **Reports** section provides:

| Report | Description |
|--------|-------------|
| **Critical Activities** | All activities on the critical path |
| **Delay Summary** | Activities with negative float or behind schedule |
| **S-Curve** | Planned vs actual progress over time |
| **Manpower Summary** | Resource loading histogram |
| **Schedule Variance** | Current vs baseline date comparison |

---

## Developer Guide

### Project Structure

```
Qplan/
├── backend/                          # FastAPI Python backend
�?  ├── app/
�?  �?  ├── __init__.py
�?  �?  ├── main.py                   # FastAPI app entry point
�?  �?  ├── api/
�?  �?  �?  └── v1/
�?  �?  �?      ├── router.py         # API router aggregation
�?  �?  �?      └── endpoints/
�?  �?  �?          ├── auth.py       # POST /auth/login, /auth/me
�?  �?  �?          ├── projects.py   # CRUD /projects
�?  �?  �?          ├── wbs.py        # CRUD /projects/{id}/wbs
�?  �?  �?          ├── activities.py # CRUD /projects/{id}/activities
�?  �?  �?          ├── relationships.py  # CRUD relationships
�?  �?  �?          ├── schedule.py   # POST /projects/{id}/schedule
�?  �?  �?          └── baselines.py  # CRUD baselines
�?  �?  ├── core/
�?  �?  �?  ├── config.py             # Pydantic settings
�?  �?  �?  ├── database.py           # SQLAlchemy engine setup
�?  �?  �?  └── auth.py               # Supabase token verification
�?  �?  ├── models/                   # SQLAlchemy ORM models (20 files)
�?  �?  �?  ├── role.py
�?  �?  �?  ├── user.py
�?  �?  �?  ├── project.py
�?  �?  �?  ├── wbs.py
�?  �?  �?  ├── activity.py
�?  �?  �?  ├── activity_relationship.py
�?  �?  �?  ├── baseline.py
�?  �?  �?  └── ... (13 more models)
�?  �?  ├── schemas/
�?  �?  �?  └── schemas.py            # Pydantic request/response schemas
�?  �?  ├── scheduling/
�?  �?  �?  └── engine.py             # CPM scheduling engine
�?  �?  └── services/
�?  �?      ├── schedule_service.py   # Schedule business logic
�?  �?      └── audit_service.py      # Audit trail logging
�?  ├── migrations/                   # Alembic migration files
�?  ├── tests/
�?  �?  └── test_cpm.py              # CPM engine unit tests
�?  ├── requirements.txt              # Python dependencies
�?  ├── Dockerfile
�?  ├── .env                          # Environment variables (gitignored)
�?  └── .env.example                  # Template for .env
�?
├── frontend/                         # React TypeScript frontend
�?  ├── src/
�?  �?  ├── main.tsx                  # React entry point
�?  �?  ├── App.tsx                   # Root component with routing
�?  �?  ├── services/
�?  �?  �?  ├── supabase.ts           # Supabase client
�?  �?  �?  └── api.ts               # Axios API client
�?  �?  ├── contexts/
�?  �?  �?  └── AuthContext.tsx        # Auth state provider
�?  �?  ├── pages/
�?  �?  �?  ├── LoginPage.tsx         # Login form
�?  �?  �?  ├── DashboardPage.tsx     # Project dashboard
�?  �?  �?  ├── ProjectWorkspace.tsx  # Main project workspace
�?  �?  �?  ├── ActivitiesPage.tsx    # Activity CRUD
�?  �?  �?  └── SchedulePage.tsx      # CPM schedule runner
�?  �?  └── vite-env.d.ts            # TypeScript env declarations
�?  ├── public/
�?  ├── package.json
�?  ├── tsconfig.json
�?  ├── vite.config.ts
�?  ├── Dockerfile
�?  ├── .env                          # Environment variables (gitignored)
�?  └── .env.example                  # Template for .env
�?
├── docker-compose.yml                # Docker orchestration
├── .gitignore
├── PRD_V1.md                         # Product Requirements Document
└── README.md                         # This file
```

### Adding a New API Endpoint

1. **Create the endpoint file** in `backend/app/api/v1/endpoints/`:

```python
# backend/app/api/v1/endpoints/my_feature.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("/")
def list_items(db: Session = Depends(get_db)):
    return {"items": []}
```

2. **Register the router** in `backend/app/api/v1/router.py`:

```python
from app.api.v1.endpoints import my_feature
api_router.include_router(my_feature.router)
```

3. **Add Pydantic schemas** in `backend/app/schemas/schemas.py` if needed.

### Adding a New Database Model

1. **Create the model** in `backend/app/models/`:

```python
# backend/app/models/my_model.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Generate a migration**:

```bash
cd backend
alembic revision --autogenerate -m "add my_table"
alembic upgrade head
```

### Adding a New Frontend Page

1. **Create the page** in `frontend/src/pages/`:

```tsx
// frontend/src/pages/MyPage.tsx
import React from 'react';
import { Card, Typography } from 'antd';

const MyPage: React.FC = () => {
  return (
    <Card>
      <Typography.Title level={3}>My Page</Typography.Title>
    </Card>
  );
};

export default MyPage;
```

2. **Add the route** in `frontend/src/App.tsx`:

```tsx
import MyPage from './pages/MyPage';
// In the routes:
<Route path="/my-page" element={<MyPage />} />
```

3. **Add navigation** in `ProjectWorkspace.tsx` sidebar if needed.

### Code Style & Conventions

- **Backend**: Python PEP 8, type hints on all functions, async where beneficial
- **Frontend**: TypeScript strict mode, functional components with hooks
- **Naming**: `snake_case` for Python, `camelCase` for TypeScript/JSX
- **Models**: One SQLAlchemy model per file in `backend/app/models/`
- **Schemas**: All Pydantic schemas in `backend/app/schemas/schemas.py`
- **Imports**: Standard library �?third-party �?local (each group separated)
- **Commits**: Use meaningful commit messages (conventional commits preferred)

---

## Deployment

### Production Deployment on Linux VPS

```bash
# 1. SSH into your server
ssh user@your-server

# 2. Clone the repository
git clone https://github.com/tms-qinst/qplan.git
cd qplan

# 3. Copy and edit production environment files
cp backend/.env.example backend/.env
nano backend/.env   # Set production values

cp frontend/.env.example frontend/.env
nano frontend/.env  # Set production values

# 4. Build and start services
docker-compose up -d --build

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Verify
curl http://localhost:8000/health
```

### Production Checklist

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Set `DEBUG=false` in backend `.env`
- [ ] Restrict `CORS_ORIGINS` to your production domain
- [ ] Set up HTTPS with a reverse proxy (nginx/Caddy)
- [ ] Configure database backups (Supabase handles this automatically)
- [ ] Review Supabase RLS policies if needed
- [ ] Set up monitoring and logging

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login with email/password |
| GET | `/api/v1/auth/me` | Get current user profile |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects` | List user's projects |
| POST | `/api/v1/projects` | Create a new project |
| GET | `/api/v1/projects/{id}` | Get project details |
| PUT | `/api/v1/projects/{id}` | Update project |

### WBS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/{id}/wbs` | List WBS nodes |
| POST | `/api/v1/projects/{id}/wbs` | Create WBS node |
| PUT | `/api/v1/wbs/{id}` | Update WBS node |
| DELETE | `/api/v1/wbs/{id}` | Delete WBS node |

### Activities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/{id}/activities` | List activities |
| POST | `/api/v1/projects/{id}/activities` | Create activity |
| PUT | `/api/v1/activities/{id}` | Update activity |
| DELETE | `/api/v1/activities/{id}` | Delete activity |

### Relationships

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/{id}/relationships` | List dependencies |
| POST | `/api/v1/relationships` | Create dependency |
| DELETE | `/api/v1/relationships/{id}` | Delete dependency |

### Schedule

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/projects/{id}/schedule` | Run CPM calculation |

**Schedule Request Body:**
```json
{
  "data_date": "2026-04-21",
  "mode": "recalculate"
}
```

**Schedule Response:**
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
      "status": "not_started"
    }
  ],
  "critical_path": ["uuid1", "uuid2"],
  "warnings": []
}
```

### Baselines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/{id}/baselines` | List baselines |
| POST | `/api/v1/projects/{id}/baselines` | Create baseline snapshot |
| GET | `/api/v1/baselines/{id}/compare` | Compare current vs baseline |

Interactive API documentation is available at **http://localhost:8000/docs** when the backend is running.

---

## Troubleshooting

### Frontend won't start

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend database connection fails

1. Check that your `.env` file has the correct `DATABASE_URL`
2. Ensure the Supabase project is active (check Supabase Dashboard)
3. Verify the password is correct
4. Test the connection:
```bash
cd backend
python -c "
from app.core.database import engine
with engine.connect() as conn:
    print('Connected successfully!')
"
```

### Docker issues

```bash
# Rebuild containers from scratch
docker-compose down -v
docker-compose up --build

# View backend logs
docker-compose logs backend

# View frontend logs
docker-compose logs frontend
```

### Migration errors

```bash
# Check current migration state
alembic current

# Reset to a specific migration
alembic downgrade <revision_id>

# Re-apply all migrations
alembic upgrade head
```

---

## Branching & Collaboration

### Branch Model

| Branch | Purpose |
|--------|---------|
| `main` | Production releases |
| `develop` | Integration / staging |
| `feature/*` | Feature development |
| `hotfix/*` | Urgent production fixes |

### Workflow

```bash
# 1. Create a feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add my new feature"

# 3. Push and create a pull request
git push origin feature/my-feature
# Create PR via GitHub targeting develop

# 4. After code review, merge the PR
```

### Rules
- �?Pull requests required for all changes
- �?Code review required before merge
- �?No direct push to `main`
- �?Never commit `.env` files with real credentials
- �?Never commit `node_modules/` or `__pycache__/`

---

## License

Proprietary �?All rights reserved.
