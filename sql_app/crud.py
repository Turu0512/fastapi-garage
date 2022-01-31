from sqlalchemy.orm import Session
from . import models, schemas
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from fastapi.params import Depends
from typing import Optional
from . import models, schemas
from fastapi import HTTPException, status


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

### ハッシュ化したパスワードの作成
def get_password_hash(password):
    return pwd_context.hash(password)

# def db_user(db: Session, user: schemas.CreateUser):
#     db_user = models.User(username= user.username)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# 新規ユーザー作成
def db_signup(db: Session, user: schemas.CreateUser):
    username = user.username
    email = user.email
    password = user.password
    overlap_user = db.query(models.User).filter(models.User.email == email).first()
    if overlap_user:
        raise HTTPException(status_code=400, detail="Email is already taken")
    if not password or len(password) < 6 :
        raise HTTPException(status_code=400, detail="Password too short")
    db_user = models.User(username=username, email=email, hashed_password=get_password_hash(password))
    db.add(db_user)
    # new_user = await db.query(models.User).filter(models.User.user_email == email).first()
    db.commit()
    db.refresh(db_user)
    return db_user

# ユーザー認証

### authenticate_userから受け取ったパスワードの確認
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

### authenticate_userの引数、DBとユーザー名をもらって検索、返す
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserInDB(**user_dict)

## ユーザーの検索、パスワードの認証をおこなう。
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_todo(db: Session, todo_id):
    return db.query(models.Todo).filter(models.Todo.todo_id == todo_id).first()


# TODO一覧を取得する
def get_todos(db:Session, skip: int = 0, limit: int =100):
    return db.query(models.Todo).offset(skip).limit(limit).all()

def get_compleat_todos(db:Session, skip: int = 0, limit: int =100):
    return db.query(models.CompleatTodo).offset(skip).limit(limit).all()


# TODO登録
def create_todo(db: Session, todo: schemas.CreateTodo):
    db_todo = models.Todo(todo_title= todo.todo_title)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# compleat_todoの移動
def compleat_todo(db: Session, todo: schemas.CreateTodo):
    db_compleat_todo = models.CompleatTodo(todo_title= todo.todo_title)
    db.add(db_compleat_todo)
    db.commit()
    db.refresh(db_compleat_todo)
    return db_compleat_todo

# TODOの削除
# def delete_todo(db: Session, todo_id: str):
#     # delete_todo = get_todo(db, todo_id)
#     todo = db.query(models.Todo).filter(models.Todo.todo_id == todo_id).first()
#     db.delete(todo)
#     db.commit()

