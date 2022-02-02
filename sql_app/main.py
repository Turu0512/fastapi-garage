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


@app.post('/signup', response_model= schemas.SignupUser)
async def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
	return crud.db_signup(db=db,user=user)

@app.post('/login')
async def login(request: OAuth2PasswordRequestForm= Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=400,detail=f"Invalid Credentials")
    
    access_token = crud.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# TODO
@app.get('/todos', response_model=List[schemas.Todo])
async def read_todo(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(crud.get_current_user)):
    todos = crud.get_todos(db, skip=skip, limit=limit)
    return todos

@app.get('/compleat_todo', response_model=List[schemas.Todo])
async def read_todo(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(crud.get_current_user)):
    compleat_todos = crud.get_compleat_todos(db, skip=skip, limit=limit)
    return compleat_todos

@app.post('/todo', response_model= schemas.CreateTodo)
async def create_todo(todo: schemas.CreateTodo, db: Session = Depends(get_db),current_user: schemas.User = Depends(crud.get_current_user)):
	return crud.create_todo(todo=todo, db=db)

@app.post('/compleat_todo', response_model= schemas.CreateTodo)
async def compleat_todo(todo: schemas.CreateTodo, db: Session = Depends(get_db), current_user: schemas.User = Depends(crud.get_current_user)):
	return crud.compleat_todo(todo=todo, db=db)

@app.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(crud.get_current_user)):
    # crud.delete_todo(todo_id, db)
    todo = db.query(models.Todo).filter(models.Todo.todo_id == todo_id).first()
    db.delete(todo)
    db.commit()

@app.delete("/compleat_todo/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(crud.get_current_user)):
    # crud.delete_todo(todo_id, db)
    todo = db.query(models.CompleatTodo).filter(models.CompleatTodo.todo_id == todo_id).first()
    db.delete(todo)
    db.commit()

