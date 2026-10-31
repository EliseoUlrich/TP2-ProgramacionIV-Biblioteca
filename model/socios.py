from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.prestamos import Prestamo


# Nivel de negocio
class SocioBase(SQLModel):
    nombre: str = Field(index=True)
    email: EmailStr = Field(unique=True, index=True)
    activo: bool = Field(default=True)


# Nivel de base de datos
class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prestamos: list["Prestamo"] = Relationship(back_populates="socio", cascade_delete=True)

