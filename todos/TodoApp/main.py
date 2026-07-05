from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
import models
from models import Todos
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status

app= FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title:str=Field(min_length=2)
    description: str=Field(min_length=3)
    priority:int=Field(gt=0)
    complete:bool=Field(default=False)


@app.get("/", status_code=status.HTTP_200_OK)
def read_all(db:db_dependency):
    return db.query(Todos).all()

@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(db: db_dependency, todo_id: int=Path(gt=0)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')

@app.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo(db:db_dependency, new_todo: TodoRequest):
    db_todo=Todos(**new_todo.model_dump())
    db.add(db_todo)
    db.commit()

@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(db:db_dependency, new_todo:TodoRequest, todo_id: int=Path(gt=0)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title=new_todo.title
    todo_model.description=new_todo.description
    todo_model.priority=new_todo.priority
    todo_model.complete=new_todo.complete
    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(db:db_dependency, todo_id: int=Path(gt=0)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todos).filter(Todos.id==todo_id).delete()
    db.commit()
    