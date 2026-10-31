# Nivel de API
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class CreateSocioRequest(SQLModel):
    nombre: str = Field(min_length=1)
    email: EmailStr
    activo: bool = True


class UpdateSocioRequest(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    activo: bool | None = None


class SocioResponse(SQLModel):
    id: int
    nombre: str
    email: EmailStr
    activo: bool


class DeleteSocioResponse(SQLModel):
    msg: str
