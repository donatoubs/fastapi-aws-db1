# database.py

from typing import List, Optional, Annotated
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine
from fastapi import Depends

# Modelo base para Libro
class BookBase(SQLModel):
    title: str = Field(index=True)
    author: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

# Modelo base para Usuario
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)

# Modelo de la tabla User en la base de datos
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    
    # La relación: Un usuario puede tener muchos libros
    books: List["Book"] = Relationship(back_populates="user")

# Modelo de la tabla Book en la base de datos
class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # La relación: Un libro pertenece a un usuario
    user: Optional[User] = Relationship(back_populates="books")

# -------------------
# Modelos para la API (DTOs - Data Transfer Objects)
# -------------------

# Modelo para leer un Libro (no mostrar el user_id)
class BookRead(BookBase):
    id: int

# Modelo para leer un Usuario (no mostrar la contraseña)
class UserRead(UserBase):
    id: int

# Modelo para leer un Usuario CON sus libros
class UserReadWithBooks(UserRead):
    books: List[BookRead] = []

# Modelo para leer un Libro CON su usuario
class BookReadWithUser(BookRead):
    user: Optional[UserRead] = None

# Modelo para crear un Usuario (se necesita la contraseña)
class UserCreate(UserBase):
    password: str

# Modelo para actualizar un Usuario (todos los campos son opcionales)
class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

# Modelo para crear un Libro
class BookCreate(BookBase):
    pass

# -------------------
# Conexión a la Base de Datos
# -------------------

rds_connection_string = "postgresql+psycopg2://postgres:Uide.asu.123@fastapi-database.cbga8yewykbk.us-east-2.rds.amazonaws.com:5432/fastapi_aws_db"

# Usamos la URL de SQLite por ahora
engine = create_engine(rds_connection_string, echo=True)

# Función para crear las tablas en la base de datos
def create_db_and_tables():
    print("Creando tablas...")
    SQLModel.metadata.create_all(engine)
    print("Tablas creadas.")

# Función para obtener una sesión de la base de datos (dependencia)
def get_session():
    with Session(engine) as session:
        yield session

# Anotación para inyectar la dependencia de la sesión en los endpoints
SessionDep = Annotated[Session, Depends(get_session)]