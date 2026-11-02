from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date, timedelta
from typing import Annotated

from fastapi import HTTPException, Query

from dependencies import LibroRepositoryDep, PrestamoRepositoryDep, SocioRepositoryDep
from model.prestamos import MULTA_POR_DIA, PLAZO_DIAS_PRESTAMO, Prestamo, PrestamoBase

MAX_PRESTAMOS_ACTIVOS = 3


class PrestamoServiceInterface(ABC):
    @abstractmethod
    def get_prestamos(self, offset: int, limit: int) -> Sequence[Prestamo]: ...

    @abstractmethod
    def get_prestamo_by_id(self, prestamo_id: int) -> Prestamo: ...

    @abstractmethod
    def get_prestamos_by_socio(self, socio_id: int, activos: bool | None) -> Sequence[Prestamo]: ...

    @abstractmethod
    def registrar_prestamo(self, socio_id: int, libro_id: int, fecha_prestamo: date | None = None) -> Prestamo: ...

    @abstractmethod
    def devolver_prestamo(self, prestamo_id: int, fecha_devolucion: date | None = None) -> Prestamo: ...


class PrestamoService(PrestamoServiceInterface):
    def __init__(
        self,
        repo: PrestamoRepositoryDep,
        socio_repo: SocioRepositoryDep,
        libro_repo: LibroRepositoryDep,
    ):
        self.repo = repo
        self.socio_repo = socio_repo
        self.libro_repo = libro_repo

    def get_prestamos(
        self,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Prestamo]:
        return self.repo.fetch_prestamos(offset, limit)

    def get_prestamo_by_id(self, prestamo_id: int) -> Prestamo:
        prestamo = self.repo.get_by_id(prestamo_id)
        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        return prestamo

    def get_prestamos_by_socio(
        self,
        socio_id: int,
        activos: bool | None = None,
    ) -> Sequence[Prestamo]:
        socio = self.socio_repo.get_by_id(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return self.repo.fetch_by_socio(socio_id, activos=activos)

    def registrar_prestamo(
        self,
        socio_id: int,
        libro_id: int,
        fecha_prestamo: date | None = None,
    ) -> Prestamo:
        # Regla 7: Recurso inexistente -> 404
        socio = self.socio_repo.get_by_id(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")

        libro = self.libro_repo.get_by_id(libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")

        # Regla 3: Un socio inactivo no puede pedir préstamos -> 403
        if not socio.activo:
            raise HTTPException(status_code=403, detail="El socio está inactivo y no puede pedir préstamos")

        # Regla 1: Un socio no puede tener más de 3 préstamos activos -> 409
        prestamos_activos = self.repo.fetch_by_socio(socio_id, activos=True)
        if len(prestamos_activos) >= MAX_PRESTAMOS_ACTIVOS:
            raise HTTPException(status_code=409, detail="El socio no puede tener más de 3 préstamos activos")

        # Regla 2: No se presta un libro sin stock; al prestar se descuenta 1 -> 409
        if libro.stock <= 0:
            raise HTTPException(status_code=409, detail="No hay stock disponible para este libro")

        # Regla 4: El plazo es de 14 días; fecha_vencimiento = fecha_prestamo + 14 días
        fecha_inicio = fecha_prestamo or date.today()
        fecha_venc = fecha_inicio + timedelta(days=PLAZO_DIAS_PRESTAMO)

        prestamo_base = PrestamoBase(
            socio_id=socio_id,
            libro_id=libro_id,
            fecha_prestamo=fecha_inicio,
            fecha_vencimiento=fecha_venc,
            fecha_devolucion=None,
            multa=0,
        )
        return self.repo.create_prestamo(prestamo_base, libro)

    def devolver_prestamo(
        self,
        prestamo_id: int,
        fecha_devolucion: date | None = None,
    ) -> Prestamo:
        # Regla 7: Recurso inexistente -> 404
        prestamo = self.repo.get_by_id(prestamo_id)
        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        # Regla 6: No se puede devolver un préstamo ya devuelto -> 409
        if prestamo.fecha_devolucion is not None:
            raise HTTPException(status_code=409, detail="No se puede devolver un préstamo ya devuelto")

        libro = self.libro_repo.get_by_id(prestamo.libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")

        # Regla 5: Al devolver se repone el stock y se calcula la multa: $100 × días de atraso (0 si llegó a tiempo)
        fecha_dev = fecha_devolucion or date.today()
        if fecha_dev < prestamo.fecha_prestamo:
            raise HTTPException(
                status_code=422,
                detail="La fecha de devolución no puede ser anterior a la fecha de préstamo",
            )
        dias_atraso = max(0, (fecha_dev - prestamo.fecha_vencimiento).days)
        multa = dias_atraso * MULTA_POR_DIA

        return self.repo.registrar_devolucion(prestamo, libro, fecha_dev, multa)
