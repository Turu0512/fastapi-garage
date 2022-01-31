from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from . import crud, models, schemas
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta


models.Base.metadata.create_all(bind=engine)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000"
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(crud.get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: schemas.User = Depends(crud.get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.post('/signup', response_model= schemas.SignupUser)
async def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
	return crud.db_signup(db=db,user=user)


# TODO
@app.get('/todos', response_model=List[schemas.Todo])
async def read_todo(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = crud.get_todos(db, skip=skip, limit=limit)
    return todos

@app.get('/compleat_todo', response_model=List[schemas.Todo])
async def read_todo(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    compleat_todos = crud.get_compleat_todos(db, skip=skip, limit=limit)
    return compleat_todos

@app.post('/todo', response_model= schemas.CreateTodo)
async def create_todo(todo: schemas.CreateTodo, db: Session = Depends(get_db)):
	return crud.create_todo(todo=todo, db=db)

@app.post('/compleat_todo', response_model= schemas.CreateTodo)
async def compleat_todo(todo: schemas.CreateTodo, db: Session = Depends(get_db)):
	return crud.compleat_todo(todo=todo, db=db)

@app.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    # crud.delete_todo(todo_id, db)
    todo = db.query(models.Todo).filter(models.Todo.todo_id == todo_id).first()
    db.delete(todo)
    db.commit()

@app.delete("/compleat_todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    # crud.delete_todo(todo_id, db)
    todo = db.query(models.CompleatTodo).filter(models.CompleatTodo.todo_id == todo_id).first()
    db.delete(todo)
    db.commit()

