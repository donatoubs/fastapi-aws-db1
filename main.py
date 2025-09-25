# main.py

from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, status

# Importar modelos y la dependencia de sesión desde database.py
from database import (
    Book,
    BookCreate,
    BookRead,
    BookReadWithUser,
    User,
    UserCreate,
    UserRead,
    UserReadWithBooks,
    UserUpdate,
    SessionDep,
    create_db_and_tables,
)

# El 'lifespan' reemplaza los eventos 'startup' y 'shutdown'.
# Se ejecuta una vez al iniciar la aplicación.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando API y creando tablas si no existen...")
    create_db_and_tables()
    yield
    print("API apagada.")

# Creación de la aplicación FastAPI
app = FastAPI(
    lifespan=lifespan,
    title="Laboratorio - API con FastAPI, EC2 y RDS",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Bienvenido": "API para el laboratorio de Cloud Computing"}

# --- Endpoints CRUD para Usuarios ---

# LÍNEA CORRECTA
@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, session: SessionDep):
    # .model_validate es la forma moderna de SQLModel para crear una instancia a partir de datos
    db_user = User.model_validate(user_in)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserReadWithBooks])
def read_users(session: SessionDep):
    users = session.query(User).all()
    return users

@app.get("/users/{user_id}", response_model=UserReadWithBooks)
def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_in: UserUpdate, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # .model_dump convierte el modelo Pydantic a un diccionario
    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    session.delete(user)
    session.commit()
    return

# --- Endpoints CRUD para Libros ---

@app.post("/books/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate, session: SessionDep):
    db_book = Book.model_validate(book_in)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[BookReadWithUser])
def read_books(session: SessionDep):
    books = session.query(Book).all()
    return books