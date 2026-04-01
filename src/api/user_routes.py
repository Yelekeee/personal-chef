from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db import crud
from src.auth.security import decode_access_token, verify_password, hash_password
from src.api.user_models import UserProfile, UpdateProfileRequest

user_router = APIRouter(prefix="/users", tags=["users"])


def _require_user(token: str, db: Session):
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Авторизация қажет.")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пайдаланушы табылмады.")
    return user


@user_router.get("/me", response_model=UserProfile)
def get_me(token: str = Query(...), db: Session = Depends(get_db)):
    user = _require_user(token, db)
    return UserProfile(user_id=user.id, email=user.email, name=user.name)


@user_router.patch("/me", response_model=UserProfile)
def update_me(body: UpdateProfileRequest, db: Session = Depends(get_db)):
    user = _require_user(body.token, db)

    new_hashed = None
    if body.new_password:
        if len(body.new_password) < 8:
            raise HTTPException(status_code=400, detail="Құпиясөз кемінде 8 таңба болуы керек.")
        if not body.current_password or not verify_password(body.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Ағымдағы құпиясөз қате.")
        new_hashed = hash_password(body.new_password)

    user = crud.update_user(db, user, name=body.name, hashed_password=new_hashed)
    return UserProfile(user_id=user.id, email=user.email, name=user.name)
