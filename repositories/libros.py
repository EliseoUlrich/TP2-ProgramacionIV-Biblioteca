from collections.abc import Sequence
from typing import Annotated

from fastapi import Query
from sqlmodel import col, select

from dependencies import SessionDep
from model.autores import Autor
from model.libros import Libro, LibroBase


class LibroRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def fetch_libros(
        self,
        disponibles: bool | None = None,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> Sequence[Libro]:
        statement = select(Libro)
        if disponibles is True:
            statement = statement.where(col(Libro.stock) > 0)
        elif disponibles is False:
            statement = statement.where(col(Libro.stock) == 0)
        statement = statement.offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create_libro(self, libro_base: LibroBase) -> Libro:
        libro = Libro(
            titulo=libro_base.titulo,
            isbn=libro_base.isbn,
            stock=libro_base.stock,
            anio=libro_base.anio,
        )
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def get_by_id(self, libro_id: int) -> Libro | None:
        return self.session.get(Libro, libro_id)

    def get_by_isbn(self, isbn: str) -> Libro | None:
        statement = select(Libro).where(col(Libro.isbn) == isbn)
        return self.session.exec(statement).first()

    def update_libro(self, libro_id: int, libro_base: LibroBase) -> Libro | None:
        libro_db = self.session.get(Libro, libro_id)
        if libro_db:
            libro_db.titulo = libro_base.titulo
            libro_db.isbn = libro_base.isbn
            libro_db.stock = libro_base.stock
            libro_db.anio = libro_base.anio
            self.session.add(libro_db)
            self.session.commit()
            self.session.refresh(libro_db)
        return libro_db

    def delete_libro(self, libro_id: int) -> None:
        libro = self.session.get(Libro, libro_id)
        if libro:
            self.session.delete(libro)
            self.session.commit()

    def add_autor(self, libro: Libro, autor: Autor) -> Libro:
        if autor not in libro.autores:
            libro.autores.append(autor)
            self.session.add(libro)
            self.session.commit()
            self.session.refresh(libro)
        return libro

    def remove_autor(self, libro: Libro, autor: Autor) -> Libro:
        if autor in libro.autores:
            libro.autores.remove(autor)
            self.session.add(libro)
            self.session.commit()
            self.session.refresh(libro)
        return libro
