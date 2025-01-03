from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True
