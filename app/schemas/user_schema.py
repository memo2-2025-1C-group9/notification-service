from pydantic import BaseModel, EmailStr


class UserInfo(BaseModel):
    name: str
    email: EmailStr
    id: int
