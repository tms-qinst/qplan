"""API v1 router aggregating all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, wbs, activities, relationships, schedule, baselines

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(wbs.router)
api_router.include_router(activities.router)
api_router.include_router(relationships.router)
api_router.include_router(schedule.router)
api_router.include_router(baselines.router)