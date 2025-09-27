from fastapi import APIRouter

from app.api.endpoints import users, consultation, templates, auth

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(consultation.router)
api_router.include_router(templates.router)