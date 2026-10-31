from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query

from api.model.prestamos import PrestamoResponse
from api.model.socios import (
    CreateSocioRequest,
    DeleteSocioResponse,
    SocioResponse,
    UpdateSocioRequest,
)
from dependencies import PrestamoServiceDep, SocioServiceDep
from model.prestamos import Prestamo
from model.socios import Socio, SocioBase

router = APIRouter(tags=["Socios"])


@router.post("/socios", response_model=SocioResponse, status_code=201)
def create_socio(req: CreateSocioRequest, service: SocioServiceDep) -> Socio:
    return service.create_socio(
        SocioBase(nombre=req.nombre, email=req.email, activo=req.activo)
    )


@router.get("/socios", response_model=Sequence[SocioResponse])
def get_socios(
    service: SocioServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Sequence[Socio]:
    return service.get_socios(offset, limit)


@router.get("/socios/{id}", response_model=SocioResponse)
def get_socio_by_id(id: int, service: SocioServiceDep) -> Socio:
    return service.get_socio_by_id(id)


@router.put("/socios/{id}", response_model=SocioResponse)
def update_socio_put(id: int, req: CreateSocioRequest, service: SocioServiceDep) -> Socio:
    return service.update_socio(
        id,
        SocioBase(nombre=req.nombre, email=req.email, activo=req.activo),
    )


@router.patch("/socios/{id}", response_model=SocioResponse)
def update_socio_patch(id: int, req: UpdateSocioRequest, service: SocioServiceDep) -> Socio:
    current = service.get_socio_by_id(id)
    socio_base = SocioBase(
        nombre=req.nombre if req.nombre is not None else current.nombre,
        email=req.email if req.email is not None else current.email,
        activo=req.activo if req.activo is not None else current.activo,
    )
    return service.update_socio(id, socio_base)


@router.delete("/socios/{id}", response_model=DeleteSocioResponse)
def delete_socio(id: int, service: SocioServiceDep) -> DeleteSocioResponse:
    service.delete_socio(id)
    return DeleteSocioResponse(msg="Socio borrado con éxito")


@router.get("/socios/{id}/prestamos", response_model=Sequence[PrestamoResponse])
def get_prestamos_socio(
    id: int,
    service: PrestamoServiceDep,
    activos: bool | None = None,
) -> Sequence[Prestamo]:
    return service.get_prestamos_by_socio(id, activos=activos)
