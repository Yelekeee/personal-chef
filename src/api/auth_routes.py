import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from src.db.database import get_db
from src.db import crud
from src.auth.security import hash_password, verify_password, create_access_token
from src.api.auth_models import (
    RegisterRequest, LoginRequest, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="Бұл email тіркелген.")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Құпиясөз кемінде 8 таңба болуы керек.")
    user = crud.create_user(db, body.email, body.name, hash_password(body.password))
    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token, user_id=user.id, name=user.name, email=user.email)


@auth_router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email немесе құпиясөз қате.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт белсенді емес.")
    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token, user_id=user.id, name=user.name, email=user.email)


@auth_router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, body.email)
    if not user:
        # Return success to avoid user enumeration
        return {"message": "Егер email тіркелген болса, хат жіберілді."}

    token = secrets.token_urlsafe(32)
    crud.create_reset_token(db, user.id, token)

    try:
        from src.email.mailer import send_reset_email
        await send_reset_email(user.email, token)
    except Exception as e:
        logger.error("SMTP send failed: %s", e, exc_info=True)

    return {"message": "Егер email тіркелген болса, хат жіберілді."}


@auth_router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset = crud.get_valid_reset_token(db, body.token)
    if not reset:
        raise HTTPException(status_code=400, detail="Сілтеме жарамсыз немесе мерзімі өтті.")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Құпиясөз кемінде 8 таңба болуы керек.")

    user = crud.get_user_by_id(db, reset.user_id)
    crud.update_user(db, user, hashed_password=hash_password(body.new_password))
    crud.mark_token_used(db, reset)
    return {"message": "Құпиясөз сәтті өзгертілді."}
