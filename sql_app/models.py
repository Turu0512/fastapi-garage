from xmlrpc.client import boolean
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

# ユーザー登録

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String, index=True)
    disabled= Column(Boolean)

class Todo(Base):
    __tablename__ = "todo"
    todo_id = Column(Integer, primary_key=True, index=True)
    todo_title = Column(String, index=True)

# class User(Base):
#     __tablename__ = "user"
#     user_id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, index=True)

class CompleatTodo(Base):
    __tablename__ = "compleat_todo"
    todo_id = Column(Integer, primary_key=True, index=True)
    todo_title = Column(String, index=True)