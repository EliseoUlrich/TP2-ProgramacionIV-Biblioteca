from datetime import date, timedelta

from sqlmodel import Field, Relationship, SQLModel

from model.libros import Libro
from model.socios import Socio

PLAZO_DIAS_PRESTAMO = 14
MULTA_POR_DIA = 100


# Nivel de negocio
class PrestamoBase(SQLModel):
    socio_id: int = Field(foreign_key="socio.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    fecha_prestamo: date = Field(default_factory=date.today)
    fecha_vencimiento: date = Field(default_factory=lambda: date.today() + timedelta(days=PLAZO_DIAS_PRESTAMO))
    fecha_devolucion: date | None = Field(default=None, nullable=True)
    multa: int = Field(default=0, ge=0)


# Nivel de base de datos
class Prestamo(PrestamoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    socio: Socio | None = Relationship(back_populates="prestamos")
    libro: Libro | None = Relationship(back_populates="prestamos")

