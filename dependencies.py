from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from repositories.database import get_session

SessionDep = Annotated[Session, Depends(get_session)]

from repositories.autores import AutorRepository  # noqa: E402

AutorRepositoryDep = Annotated[AutorRepository, Depends(AutorRepository)]

from repositories.libros import LibroRepository  # noqa: E402

LibroRepositoryDep = Annotated[LibroRepository, Depends(LibroRepository)]

from repositories.socios import SocioRepository  # noqa: E402

SocioRepositoryDep = Annotated[SocioRepository, Depends(SocioRepository)]

from repositories.prestamos import PrestamoRepository  # noqa: E402

PrestamoRepositoryDep = Annotated[PrestamoRepository, Depends(PrestamoRepository)]

from services.autores import AutorService, AutorServiceInterface  # noqa: E402

AutorServiceDep = Annotated[AutorServiceInterface, Depends(AutorService)]

from services.libros import LibroService, LibroServiceInterface  # noqa: E402

LibroServiceDep = Annotated[LibroServiceInterface, Depends(LibroService)]

from services.socios import SocioService, SocioServiceInterface  # noqa: E402

SocioServiceDep = Annotated[SocioServiceInterface, Depends(SocioService)]

from services.prestamos import PrestamoService, PrestamoServiceInterface  # noqa: E402

PrestamoServiceDep = Annotated[PrestamoServiceInterface, Depends(PrestamoService)]
