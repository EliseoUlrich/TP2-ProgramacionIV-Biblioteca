# Nivel de API
from datetime import date

from sqlmodel import SQLModel


class CreatePrestamoRequest(SQLModel):
    socio_id: int
    libro_id: int
    fecha_prestamo: date | None = None


class DevolucionPrestamoRequest(SQLModel):
    fecha_devolucion: date | None = None


class PrestamoResponse(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
    multa: int

