# Nivel de API
from sqlmodel import Field, SQLModel

from api.model.autores import AutorResponse


class CreateLibroRequest(SQLModel):
    titulo: str = Field(min_length=1)
    isbn: str = Field(min_length=1)
    stock: int = Field(default=0, ge=0)
    anio: int


class UpdateLibroRequest(SQLModel):
    titulo: str | None = Field(default=None, min_length=1)
    isbn: str | None = Field(default=None, min_length=1)
    stock: int | None = Field(default=None, ge=0)
    anio: int | None = None


class LibroResponse(SQLModel):
    id: int
    titulo: str
    isbn: str
    stock: int
    anio: int


class LibroResponseWithAutores(LibroResponse):
    autores: list[AutorResponse] = []


class DeleteLibroResponse(SQLModel):
    msg: str
