from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.core.roles import serialize_roles

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(
    db: Session,
    user: UserCreate,
    initial_role: str = "Nurse",
    *,
    commit: bool = True,
):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, role=initial_role)
    db.add(db_user)
    if commit:
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user_roles(db: Session, user: User, roles: list[str]):
    user.role = serialize_roles(roles)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
