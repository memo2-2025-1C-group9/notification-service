from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, user_id: int):
    existing_user = get_user_by_id(db, user_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está registrado",
        )

    new_user = User(id=user_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
