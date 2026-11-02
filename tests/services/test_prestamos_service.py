from datetime import date

from fastapi import HTTPException
import pytest
from sqlmodel import Session

from repositories.autores import AutorRepository
from repositories.libros import LibroRepository
from repositories.prestamos import PrestamoRepository
from repositories.socios import SocioRepository
from services.libros import LibroService
from services.prestamos import PrestamoService


def _build_prestamo_service(session: Session) -> PrestamoService:
    return PrestamoService(
        repo=PrestamoRepository(session),
        socio_repo=SocioRepository(session),
        libro_repo=LibroRepository(session),
    )


def test_service_reglas_negocio_en_capa_services(session: Session, seed):
    service = _build_prestamo_service(session)

    # Préstamo válido
    prestamo = service.registrar_prestamo(socio_id=1, libro_id=1, fecha_prestamo=date(2026, 4, 1))
    assert prestamo.fecha_vencimiento == date(2026, 4, 15)

    # Devolución con 3 días de atraso -> $300
    devuelto = service.devolver_prestamo(prestamo.id, fecha_devolucion=date(2026, 4, 18))  # type: ignore[arg-type]
    assert devuelto.multa == 300

    # No se puede devolver dos veces (Regla 6 -> 409)
    with pytest.raises(HTTPException) as exc:
        service.devolver_prestamo(prestamo.id)  # type: ignore[arg-type]
    assert exc.value.status_code == 409

    # Consulta de préstamos por libro (todos, activos e inactivos)
    prestamo_repo = PrestamoRepository(session)
    assert len(prestamo_repo.fetch_by_libro(1)) == 1
    assert len(prestamo_repo.fetch_by_libro(1, activos=True)) == 0
    assert len(prestamo_repo.fetch_by_libro(1, activos=False)) == 1


def test_service_libro_isbn_duplicado(session: Session, seed):
    from model.libros import LibroBase

    libro_service = LibroService(
        repo=LibroRepository(session),
        autor_repo=AutorRepository(session),
        prestamo_repo=PrestamoRepository(session),
    )
    with pytest.raises(HTTPException) as exc:
        libro_service.create_libro(
            LibroBase(titulo="Duplicado", isbn="978-84-206-6655-6", stock=1, anio=2024)
        )
    assert exc.value.status_code == 409

