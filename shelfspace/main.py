from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, Field

app=FastAPI()

class BookCreate(BaseModel):
    title: str=Field(min_length=3)
    author: str=Field(min_length=2)
    rating: int=Field(gt=0, le=5)
    is_read: bool=Field(default=False)

class Book(BookCreate):
    id: int=Field(gt=0)

books=[]

@app.post("/books")
def create_book(book: BookCreate):
    new_book=Book(id=len(books)+1, **book.model_dump())
    books.append(new_book)
    return new_book

@app.get("/books/")
def get_book(is_read: Optional[bool]=None):
    if is_read is None:
        return books
    return [
        bk for bk in books if bk.is_read==is_read
    ]

@app.get("/books/{book_id}")
def get_one_book(book_id:int):
    for bk in books:
        if bk.id==book_id:
            return bk
    raise HTTPException(statuscode=404, detail="Book ID not found") 

app.