from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query

from api.model.libros import (
    CreateLibroRequest,
    DeleteLibroResponse,
    LibroResponseWithAutores,
    UpdateLibroRequest,
)
from dependencies import LibroServiceDep
from model.libros import Libro, LibroBase

router = APIRouter(tags=["Libros"])


@router.post("/libros", response_model=LibroResponseWithAutores, status_code=201)
def create_libro(req: CreateLibroRequest, service: LibroServiceDep) -> Libro:
    return service.create_libro(
        LibroBase(titulo=req.titulo, isbn=req.isbn, stock=req.stock, anio=req.anio)
    )


@router.get("/libros", response_model=Sequence[LibroResponseWithAutores])
def get_libros(
    service: LibroServiceDep,
    disponibles: bool | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Sequence[Libro]:
    return service.get_libros(disponibles=disponibles, offset=offset, limit=limit)


@router.get("/libros/{id}", response_model=LibroResponseWithAutores)
def get_libro_by_id(id: int, service: LibroServiceDep) -> Libro:
    return service.get_libro_by_id(id)


@router.put("/libros/{id}", response_model=LibroResponseWithAutores)
def update_libro_put(id: int, req: CreateLibroRequest, service: LibroServiceDep) -> Libro:
    return service.update_libro(
        id,
        LibroBase(titulo=req.titulo, isbn=req.isbn, stock=req.stock, anio=req.anio),
    )


@router.patch("/libros/{id}", response_model=LibroResponseWithAutores)
def update_libro_patch(id: int, req: UpdateLibroRequest, service: LibroServiceDep) -> Libro:
    current = service.get_libro_by_id(id)
    libro_base = LibroBase(
        titulo=req.titulo if req.titulo is not None else current.titulo,
        isbn=req.isbn if req.isbn is not None else current.isbn,
        stock=req.stock if req.stock is not None else current.stock,
        anio=req.anio if req.anio is not None else current.anio,
    )
    return service.update_libro(id, libro_base)


@router.delete("/libros/{id}", response_model=DeleteLibroResponse)
def delete_libro(id: int, service: LibroServiceDep) -> DeleteLibroResponse:
    service.delete_libro(id)
    return DeleteLibroResponse(msg="Libro borrado con éxito")


@router.post("/libros/{id}/autores/{autor_id}", response_model=LibroResponseWithAutores)
def asociar_autor_a_libro(id: int, autor_id: int, service: LibroServiceDep) -> Libro:
    return service.asociar_autor(id, autor_id)


@router.delete("/libros/{id}/autores/{autor_id}", response_model=LibroResponseWithAutores)
def desasociar_autor_de_libro(id: int, autor_id: int, service: LibroServiceDep) -> Libro:
    return service.desasociar_autor(id, autor_id)
