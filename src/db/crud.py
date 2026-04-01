import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from src.db.models import User, EmotionScan, ChatSession, ChatMessage, PasswordResetToken


# ── Users ───────────────────────────────────────────────────────────────────


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, name: str, hashed_password: str) -> User:
    user = User(email=email.lower(), name=name, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, name: str | None = None, hashed_password: str | None = None) -> User:
    if name is not None:
        user.name = name
    if hashed_password is not None:
        user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user


# ── Emotion Scans ────────────────────────────────────────────────────────────


def save_emotion_scan(
    db: Session,
    user_id: str,
    scan_method: str,
    emotion: str,
    level: str,
    confidence: float,
    analysis: str,
    recommendations: list[str],
    mental_health_note: str | None,
) -> EmotionScan:
    scan = EmotionScan(
        user_id=user_id,
        scan_method=scan_method,
        emotion=emotion,
        level=level,
        confidence=confidence,
        analysis=analysis,
        recommendations=json.dumps(recommendations, ensure_ascii=False),
        mental_health_note=mental_health_note,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def get_scans_for_user(db: Session, user_id: str) -> list[EmotionScan]:
    return (
        db.query(EmotionScan)
        .filter(EmotionScan.user_id == user_id)
        .order_by(EmotionScan.scanned_at.desc())
        .all()
    )


def delete_scans_for_user(db: Session, user_id: str) -> None:
    db.query(EmotionScan).filter(EmotionScan.user_id == user_id).delete()
    db.commit()


# ── Chat Sessions ────────────────────────────────────────────────────────────


def create_chat_session(db: Session, user_id: str, title: str = "Жаңа әңгіме") -> ChatSession:
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_chat_sessions_for_user(db: Session, user_id: str) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def get_chat_session(db: Session, session_id: str, user_id: str) -> ChatSession | None:
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def update_session_title(db: Session, session: ChatSession, title: str) -> ChatSession:
    session.title = title
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session


def delete_chat_session(db: Session, session: ChatSession) -> None:
    db.delete(session)
    db.commit()


# ── Chat Messages ────────────────────────────────────────────────────────────


def add_message(db: Session, session_id: str, role: str, content: str) -> ChatMessage:
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages_for_session(db: Session, session_id: str) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.sent_at.asc())
        .all()
    )


# ── Password Reset Tokens ────────────────────────────────────────────────────


def create_reset_token(db: Session, user_id: str, token: str, expires_minutes: int = 60) -> PasswordResetToken:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    reset = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(reset)
    db.commit()
    db.refresh(reset)
    return reset


def get_valid_reset_token(db: Session, token: str) -> PasswordResetToken | None:
    now = datetime.now(timezone.utc)
    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,  # noqa: E712
            PasswordResetToken.expires_at > now,
        )
        .first()
    )


def mark_token_used(db: Session, reset: PasswordResetToken) -> None:
    reset.used = True
    db.commit()
