from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Annotated

from fastapi import HTTPException, Query

from dependencies import PrestamoRepositoryDep, SocioRepositoryDep
from model.socios import Socio, SocioBase


class SocioServiceInterface(ABC):
    @abstractmethod
    def get_socios(self, offset: int, limit: int) -> Sequence[Socio]: ...

    @abstractmethod
    def get_socio_by_id(self, socio_id: int) -> Socio: ...

    @abstractmethod
    def create_socio(self, socio_base: SocioBase) -> Socio: ...

    @abstractmethod
    def update_socio(self, socio_id: int, socio_base: SocioBase) -> Socio: ...

    @abstractmethod
    def delete_socio(self, socio_id: int) -> None: ...


class SocioService(SocioServiceInterface):
    def __init__(
        self,
        repo: SocioRepositoryDep,
        prestamo_repo: PrestamoRepositoryDep,
    ):
        self.repo = repo
        self.prestamo_repo = prestamo_repo

    def get_socios(
        self,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Socio]:
        return self.repo.fetch_socios(offset, limit)

    def get_socio_by_id(self, socio_id: int) -> Socio:
        socio = self.repo.get_by_id(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return socio

    def create_socio(self, socio_base: SocioBase) -> Socio:
        if self.repo.get_by_email(str(socio_base.email)):
            raise HTTPException(status_code=409, detail="El email ya está registrado")
        return self.repo.create_socio(socio_base)

    def update_socio(self, socio_id: int, socio_base: SocioBase) -> Socio:
        existing = self.repo.get_by_email(str(socio_base.email))
        if existing and existing.id != socio_id:
            raise HTTPException(status_code=409, detail="El email ya está registrado")
        updated = self.repo.update_socio(socio_id, socio_base)
        if not updated:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return updated

    def delete_socio(self, socio_id: int) -> None:
        if not self.repo.get_by_id(socio_id):
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        if self.prestamo_repo.fetch_by_socio(socio_id, activos=True):
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar un socio con préstamos activos",
            )
        self.repo.delete_socio(socio_id)
