from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import app, on_startup
from model.autores import Autor
from model.libros import Libro
from model.socios import Socio
from repositories import database
from repositories.database import get_session
from repositories.seed import seed_biblioteca


def test_seed_creates_initial_data(session: Session):
    seed_biblioteca(session)
    autores = session.exec(select(Autor)).all()
    libros = session.exec(select(Libro)).all()
    socios = session.exec(select(Socio)).all()

    assert len(autores) == 3
    assert len(libros) == 3
    assert len(socios) == 3


def test_seed_is_idempotent(session: Session):
    seed_biblioteca(session)
    seed_biblioteca(session)
    assert len(session.exec(select(Autor)).all()) == 3
    assert len(session.exec(select(Libro)).all()) == 3
    assert len(session.exec(select(Socio)).all()) == 3


def test_database_and_startup(session: Session, monkeypatch):
    monkeypatch.setattr(database, "engine", session.get_bind())
    on_startup()
    gen = get_session()
    db_session = next(gen)
    assert db_session is not None
    gen.close()

    with TestClient(app) as c:
        res = c.get("/autores")
        assert res.status_code == 200
        assert len(res.json()) == 3

