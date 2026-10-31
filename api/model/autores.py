# Nivel de API
from sqlmodel import Field, SQLModel


class CreateAutorRequest(SQLModel):
    nombre: str = Field(min_length=1)
    nacionalidad: str = Field(min_length=1)


class UpdateAutorRequest(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    nacionalidad: str | None = Field(default=None, min_length=1)


class AutorResponse(SQLModel):
    id: int
    nombre: str
    nacionalidad: str


class DeleteAutorResponse(SQLModel):
    msg: str
