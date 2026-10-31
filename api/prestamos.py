from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Body, Query

from api.model.prestamos import (
    CreatePrestamoRequest,
    DevolucionPrestamoRequest,
    PrestamoResponse,
)
from dependencies import PrestamoServiceDep
from model.prestamos import Prestamo

router = APIRouter(tags=["Préstamos"])


@router.post("/prestamos", response_model=PrestamoResponse, status_code=201)
def create_prestamo(req: CreatePrestamoRequest, service: PrestamoServiceDep) -> Prestamo:
    return service.registrar_prestamo(
        socio_id=req.socio_id,
        libro_id=req.libro_id,
        fecha_prestamo=req.fecha_prestamo,
    )


@router.get("/prestamos", response_model=Sequence[PrestamoResponse])
def get_prestamos(
    service: PrestamoServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Sequence[Prestamo]:
    return service.get_prestamos(offset, limit)


@router.get("/prestamos/{id}", response_model=PrestamoResponse)
def get_prestamo_by_id(id: int, service: PrestamoServiceDep) -> Prestamo:
    return service.get_prestamo_by_id(id)


@router.post("/prestamos/{id}/devolucion", response_model=PrestamoResponse)
def devolver_prestamo(
    id: int,
    service: PrestamoServiceDep,
    req: Annotated[DevolucionPrestamoRequest | None, Body()] = None,
) -> Prestamo:
    fecha_dev = req.fecha_devolucion if req else None
    return service.devolver_prestamo(prestamo_id=id, fecha_devolucion=fecha_dev)
