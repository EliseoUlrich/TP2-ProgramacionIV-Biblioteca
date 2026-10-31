from collections.abc import Sequence
from datetime import date
from typing import Annotated

from fastapi import Query
from sqlmodel import col, select

from dependencies import SessionDep
from model.libros import Libro
from model.prestamos import Prestamo, PrestamoBase


class PrestamoRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def fetch_prestamos(
        self,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Prestamo]:
        statement = select(Prestamo).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_by_id(self, prestamo_id: int) -> Prestamo | None:
        return self.session.get(Prestamo, prestamo_id)

    def fetch_by_socio(
        self,
        socio_id: int,
        activos: bool | None = None,
    ) -> Sequence[Prestamo]:
        statement = select(Prestamo).where(col(Prestamo.socio_id) == socio_id)
        if activos is True:
            statement = statement.where(col(Prestamo.fecha_devolucion).is_(None))
        elif activos is False:
            statement = statement.where(col(Prestamo.fecha_devolucion).is_not(None))
        return self.session.exec(statement).all()

    def create_prestamo(self, prestamo_base: PrestamoBase, libro: Libro) -> Prestamo:
        libro.stock -= 1
        prestamo = Prestamo(
            socio_id=prestamo_base.socio_id,
            libro_id=prestamo_base.libro_id,
            fecha_prestamo=prestamo_base.fecha_prestamo,
            fecha_vencimiento=prestamo_base.fecha_vencimiento,
            fecha_devolucion=None,
            multa=0,
        )
        self.session.add(libro)
        self.session.add(prestamo)
        self.session.commit()
        self.session.refresh(prestamo)
        self.session.refresh(libro)
        return prestamo

    def registrar_devolucion(
        self,
        prestamo: Prestamo,
        libro: Libro,
        fecha_devolucion: date,
        multa: int,
    ) -> Prestamo:
        prestamo.fecha_devolucion = fecha_devolucion
        prestamo.multa = multa
        libro.stock += 1
        self.session.add(prestamo)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(prestamo)
        self.session.refresh(libro)
        return prestamo
