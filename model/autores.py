from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.libros import Libro


# Tabla intermedia Libro <-> Autor (muchos a muchos)
class LibroAutor(SQLModel, table=True):
    libro_id: int | None = Field(default=None, foreign_key="libro.id", primary_key=True)
    autor_id: int | None = Field(default=None, foreign_key="autor.id", primary_key=True)


# Nivel de negocio
class AutorBase(SQLModel):
    nombre: str = Field(index=True)
    nacionalidad: str


# Nivel de base de datos
class Autor(AutorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    libros: list["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)

