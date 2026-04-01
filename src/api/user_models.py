from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    name: str


class UpdateProfileRequest(BaseModel):
    token: str
    name: str | None = None
    new_password: str | None = None
    current_password: str | None = None
