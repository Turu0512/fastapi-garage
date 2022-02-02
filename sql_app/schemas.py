from pydantic import BaseModel, Field
from typing import Optional


class CreateTodo(BaseModel):
    todo_title: str = Field(max_length=12)
    class Config:
        orm_mode = True

class Todo(CreateTodo):
    todo_id: int

class DeleteTodo(BaseModel):
    todo_id: int

# JWT認証、トークン
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class CreateUser(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    class Config:
        orm_mode = True

class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None
    class Config:
        orm_mode = True

class LoginUser(BaseModel):
    username: str
    password: str

class SignupUser(User):
    user_id: int
    hashed_password: str


class UserInDB(User):
    hashed_password: str
