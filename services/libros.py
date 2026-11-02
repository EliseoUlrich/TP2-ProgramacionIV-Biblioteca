from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Annotated

from fastapi import HTTPException, Query

from dependencies import AutorRepositoryDep, LibroRepositoryDep, PrestamoRepositoryDep
from model.libros import Libro, LibroBase


class LibroServiceInterface(ABC):
    @abstractmethod
    def get_libros(self, disponibles: bool | None, offset: int, limit: int) -> Sequence[Libro]: ...

    @abstractmethod
    def get_libro_by_id(self, libro_id: int) -> Libro: ...

    @abstractmethod
    def create_libro(self, libro_base: LibroBase) -> Libro: ...

    @abstractmethod
    def update_libro(self, libro_id: int, libro_base: LibroBase) -> Libro: ...

    @abstractmethod
    def delete_libro(self, libro_id: int) -> None: ...

    @abstractmethod
    def asociar_autor(self, libro_id: int, autor_id: int) -> Libro: ...

    @abstractmethod
    def desasociar_autor(self, libro_id: int, autor_id: int) -> Libro: ...


class LibroService(LibroServiceInterface):
    def __init__(
        self,
        repo: LibroRepositoryDep,
        autor_repo: AutorRepositoryDep,
        prestamo_repo: PrestamoRepositoryDep,
    ):
        self.repo = repo
        self.autor_repo = autor_repo
        self.prestamo_repo = prestamo_repo

    def get_libros(
        self,
        disponibles: bool | None = None,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Libro]:
        return self.repo.fetch_libros(disponibles=disponibles, offset=offset, limit=limit)

    def get_libro_by_id(self, libro_id: int) -> Libro:
        libro = self.repo.get_by_id(libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return libro

    def create_libro(self, libro_base: LibroBase) -> Libro:
        if self.repo.get_by_isbn(libro_base.isbn):
            raise HTTPException(status_code=409, detail="El ISBN ya está registrado")
        return self.repo.create_libro(libro_base)

    def update_libro(self, libro_id: int, libro_base: LibroBase) -> Libro:
        existing = self.repo.get_by_isbn(libro_base.isbn)
        if existing and existing.id != libro_id:
            raise HTTPException(status_code=409, detail="El ISBN ya está registrado")
        updated = self.repo.update_libro(libro_id, libro_base)
        if not updated:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return updated

    def delete_libro(self, libro_id: int) -> None:
        if not self.repo.get_by_id(libro_id):
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        if self.prestamo_repo.fetch_by_libro(libro_id, activos=True):
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar un libro con préstamos activos",
            )
        self.repo.delete_libro(libro_id)

    def asociar_autor(self, libro_id: int, autor_id: int) -> Libro:
        libro = self.repo.get_by_id(libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        autor = self.autor_repo.get_by_id(autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        return self.repo.add_autor(libro, autor)

    def desasociar_autor(self, libro_id: int, autor_id: int) -> Libro:
        libro = self.repo.get_by_id(libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        autor = self.autor_repo.get_by_id(autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        return self.repo.remove_autor(libro, autor)
