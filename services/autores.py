from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Annotated

from fastapi import HTTPException, Query

from dependencies import AutorRepositoryDep
from model.autores import Autor, AutorBase


class AutorServiceInterface(ABC):
    @abstractmethod
    def get_autores(self, offset: int, limit: int) -> Sequence[Autor]: ...

    @abstractmethod
    def get_autor_by_id(self, autor_id: int) -> Autor: ...

    @abstractmethod
    def create_autor(self, autor_base: AutorBase) -> Autor: ...

    @abstractmethod
    def update_autor(self, autor_id: int, autor_base: AutorBase) -> Autor: ...

    @abstractmethod
    def delete_autor(self, autor_id: int) -> None: ...


class AutorService(AutorServiceInterface):
    def __init__(self, repo: AutorRepositoryDep):
        self.repo = repo

    def get_autores(
        self,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Autor]:
        return self.repo.fetch_autores(offset, limit)

    def get_autor_by_id(self, autor_id: int) -> Autor:
        autor = self.repo.get_by_id(autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        return autor

    def create_autor(self, autor_base: AutorBase) -> Autor:
        return self.repo.create_autor(autor_base)

    def update_autor(self, autor_id: int, autor_base: AutorBase) -> Autor:
        updated = self.repo.update_autor(autor_id, autor_base)
        if not updated:
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        return updated

    def delete_autor(self, autor_id: int) -> None:
        if not self.repo.get_by_id(autor_id):
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        self.repo.delete_autor(autor_id)
