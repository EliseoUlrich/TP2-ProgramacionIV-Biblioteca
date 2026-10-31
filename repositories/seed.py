from sqlmodel import Session, select

from model.autores import Autor
from model.libros import Libro
from model.socios import Socio


def seed_biblioteca(session: Session) -> None:
    if session.exec(select(Autor)).first():
        return

    borges = Autor(nombre="Jorge Luis Borges", nacionalidad="Argentina")
    garcia_marquez = Autor(nombre="Gabriel García Márquez", nacionalidad="Colombia")
    cortazar = Autor(nombre="Julio Cortázar", nacionalidad="Argentina")
    session.add_all([borges, garcia_marquez, cortazar])
    session.commit()
    session.refresh(borges)
    session.refresh(garcia_marquez)
    session.refresh(cortazar)

    libros = [
        Libro(titulo="Ficciones", isbn="978-84-206-6655-6", stock=3, anio=1944, autores=[borges]),
        Libro(titulo="Cien años de soledad", isbn="978-84-376-0494-7", stock=2, anio=1967, autores=[garcia_marquez]),
        Libro(titulo="Rayuela", isbn="978-84-376-0457-2", stock=0, anio=1963, autores=[cortazar]),
    ]
    session.add_all(libros)

    socios = [
        Socio(nombre="Martina Gómez", email="mgomez@email.com", activo=True),
        Socio(nombre="Santiago Fernández", email="sfer@email.com", activo=True),
        Socio(nombre="Camila Martínez", email="cma@email.com", activo=False),
    ]
    session.add_all(socios)
    session.commit()
