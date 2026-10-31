from collections.abc import Sequence
from typing import Annotated

from fastapi import Query
from sqlmodel import select

from dependencies import SessionDep
from model.autores import Autor, AutorBase


class AutorRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def fetch_autores(
        self,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Autor]:
        statement = select(Autor).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create_autor(self, autor_base: AutorBase) -> Autor:
        autor = Autor(nombre=autor_base.nombre, nacionalidad=autor_base.nacionalidad)
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def get_by_id(self, autor_id: int) -> Autor | None:
        return self.session.get(Autor, autor_id)

    def update_autor(self, autor_id: int, autor_base: AutorBase) -> Autor | None:
        autor_db = self.session.get(Autor, autor_id)
        if autor_db:
            autor_db.nombre = autor_base.nombre
            autor_db.nacionalidad = autor_base.nacionalidad
            self.session.add(autor_db)
            self.session.commit()
            self.session.refresh(autor_db)
        return autor_db

    def delete_autor(self, autor_id: int) -> None:
        autor = self.session.get(Autor, autor_id)
        if autor:
            self.session.delete(autor)
            self.session.commit()
