from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query

from api.model.autores import (
    AutorResponse,
    CreateAutorRequest,
    DeleteAutorResponse,
    UpdateAutorRequest,
)
from dependencies import AutorServiceDep
from model.autores import Autor, AutorBase

router = APIRouter(tags=["Autores"])


@router.post("/autores", response_model=AutorResponse, status_code=201)
def create_autor(req: CreateAutorRequest, service: AutorServiceDep) -> Autor:
    return service.create_autor(AutorBase(nombre=req.nombre, nacionalidad=req.nacionalidad))


@router.get("/autores", response_model=Sequence[AutorResponse])
def get_autores(
    service: AutorServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Sequence[Autor]:
    return service.get_autores(offset, limit)


@router.get("/autores/{id}", response_model=AutorResponse)
def get_autor_by_id(id: int, service: AutorServiceDep) -> Autor:
    return service.get_autor_by_id(id)


@router.put("/autores/{id}", response_model=AutorResponse)
def update_autor_put(id: int, req: CreateAutorRequest, service: AutorServiceDep) -> Autor:
    return service.update_autor(id, AutorBase(nombre=req.nombre, nacionalidad=req.nacionalidad))


@router.patch("/autores/{id}", response_model=AutorResponse)
def update_autor_patch(id: int, req: UpdateAutorRequest, service: AutorServiceDep) -> Autor:
    current = service.get_autor_by_id(id)
    autor_base = AutorBase(
        nombre=req.nombre if req.nombre is not None else current.nombre,
        nacionalidad=req.nacionalidad if req.nacionalidad is not None else current.nacionalidad,
    )
    return service.update_autor(id, autor_base)


@router.delete("/autores/{id}", response_model=DeleteAutorResponse)
def delete_autor(id: int, service: AutorServiceDep) -> DeleteAutorResponse:
    service.delete_autor(id)
    return DeleteAutorResponse(msg="Autor borrado con éxito")
