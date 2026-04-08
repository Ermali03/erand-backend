from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.db.database import SessionLocal
from app.crud import user as crud_user
from app.schemas.user import UserCreate


def bootstrap_initial_admin() -> None:
    if not settings.CREATE_INITIAL_ADMIN:
        return
    if not settings.INITIAL_ADMIN_EMAIL or not settings.INITIAL_ADMIN_PASSWORD:
        raise RuntimeError(
            "CREATE_INITIAL_ADMIN is enabled but INITIAL_ADMIN_EMAIL or "
            "INITIAL_ADMIN_PASSWORD is missing."
        )
    db = SessionLocal()
    try:
        user = crud_user.get_user_by_email(db, email=settings.INITIAL_ADMIN_EMAIL)
        if not user:
            admin_in = UserCreate(
                email=settings.INITIAL_ADMIN_EMAIL,
                password=settings.INITIAL_ADMIN_PASSWORD,
            )
            crud_user.create_user(db, user=admin_in, initial_role="Admin")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_initial_admin()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
def healthcheck():
    return {"status": "ok", "service": settings.PROJECT_NAME}
