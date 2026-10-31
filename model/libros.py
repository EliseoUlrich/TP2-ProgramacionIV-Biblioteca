from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from model.autores import Autor, LibroAutor

if TYPE_CHECKING:
    from model.prestamos import Prestamo


# Nivel de negocio
class LibroBase(SQLModel):
    titulo: str = Field(index=True)
    isbn: str = Field(unique=True, index=True)
    stock: int = Field(default=0, ge=0)
    anio: int


# Nivel de base de datos
class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    autores: list[Autor] = Relationship(back_populates="libros", link_model=LibroAutor)
    prestamos: list["Prestamo"] = Relationship(back_populates="libro", cascade_delete=True)

