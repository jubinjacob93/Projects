from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel, Field

app=FastAPI()

class BookCreate(BaseModel):
    title: str=Field(min_length=3)
    author: str=Field(min_length=2)
    rating: Optional[int]=Field(default=None, ge=1, le=5)
    is_read: bool=Field(default=False)

class BookUpdate(BaseModel):
    title: Optional[str]=Field(min_length=3)
    author: Optional[str]=Field(min_length=2)
    rating: Optional[int]=Field(gt=0, le=5)
    is_read: Optional[bool]=Field(default=None)

class Book(BookCreate):
    id: int=Field(gt=0)

books=[]

@app.post("/books")
def create_book(book: BookCreate):
    new_book=Book(id=len(books)+1, **book.model_dump())
    books.append(new_book)
    return new_book

@app.get("/books/")
def get_books(is_read: Optional[bool]=None):
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
    raise HTTPException(status_code=404, detail="Book ID not found") 

@app.patch("/books/{book_id}")
def update_book(book_id:int, book:BookUpdate):
    updated_book=book.model_dump(exclude_unset=True)
    for bk in books:
        if bk.id==book_id:
            if bk.rating is None and book.rating is None and book.is_read is True:
                raise HTTPException(status_code=400, detail="Finished books need to have a rating")
            for key, value in updated_book.items():
                setattr(bk, key, value)
            return bk
    raise HTTPException(status_code=404, detail="Book ID not found")


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for ix, bk in enumerate(books):
        if bk.id==book_id:
            books.pop(ix)
            return {"message": "Book deleted"}
    raise HTTPException(status_code=404, detail="Book ID not found")
