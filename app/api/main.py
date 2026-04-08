from fastapi import APIRouter
from app.api.routes import auth, users, clinic, records

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clinic.router, tags=["clinic"])
api_router.include_router(records.router, tags=["records"])
