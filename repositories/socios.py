from collections.abc import Sequence
from typing import Annotated

from fastapi import Query
from sqlmodel import col, select

from dependencies import SessionDep
from model.socios import Socio, SocioBase


class SocioRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def fetch_socios(
        self,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Socio]:
        statement = select(Socio).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create_socio(self, socio_base: SocioBase) -> Socio:
        socio = Socio(
            nombre=socio_base.nombre,
            email=socio_base.email,
            activo=socio_base.activo,
        )
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def get_by_id(self, socio_id: int) -> Socio | None:
        return self.session.get(Socio, socio_id)

    def get_by_email(self, email: str) -> Socio | None:
        statement = select(Socio).where(col(Socio.email) == email)
        return self.session.exec(statement).first()

    def update_socio(self, socio_id: int, socio_base: SocioBase) -> Socio | None:
        socio_db = self.session.get(Socio, socio_id)
        if socio_db:
            socio_db.nombre = socio_base.nombre
            socio_db.email = socio_base.email
            socio_db.activo = socio_base.activo
            self.session.add(socio_db)
            self.session.commit()
            self.session.refresh(socio_db)
        return socio_db

    def delete_socio(self, socio_id: int) -> None:
        socio = self.session.get(Socio, socio_id)
        if socio:
            self.session.delete(socio)
            self.session.commit()
