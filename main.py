import logging

from fastapi import FastAPI
from sqlmodel import Session

from api import autores, libros, prestamos, socios
from repositories import database
from repositories.database import create_db_and_tables
from repositories.seed import seed_biblioteca

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

app = FastAPI()
app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)
app.include_router(prestamos.router)


def create_seed_data():
    with Session(database.engine) as session:
        seed_biblioteca(session)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    create_seed_data()
