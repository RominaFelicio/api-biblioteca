from pathlib import Path
import json
import logging

from pydantic import BaseModel, ConfigDict, Field
from fastapi import FastAPI, HTTPException

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

 
app = FastAPI(title="API mi biblioteca");



CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_DATOS = CARPETA_PROYECTO / "datos"

ARCHIVO_LIBROS = CARPETA_DATOS / "libros.json"

class LibroEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True

class LibroActualizacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(default=None, min_length=3, max_length=100)
    autor: str | None = Field(default=None, min_length=3, max_length=60)
    anio: int | None = Field(default=None, ge=1000, le=2100)
    disponible: bool | None = None

class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    anio: int
    disponible: bool

# PERSISTENCIA JSON

libros = []
siguiente_id = 1


def cargar_libros():
    global libros, siguiente_id

    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)

    if not ARCHIVO_LIBROS.exists():
        libros = []
        siguiente_id = 1
        return

    try:
        with ARCHIVO_LIBROS.open("r", encoding="utf-8") as archivo:
            contenido = json.load(archivo)

        if not isinstance(contenido, list):
            raise ValueError("El archivo debe contener una lista.")

        libros = [
            Libro.model_validate(item).model_dump()
            for item in contenido
        ]

        libros.sort(key=lambda libro: libro["id"])
        siguiente_id = max(
            (libro["id"] for libro in libros),
            default=0
        ) + 1

    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        libros = []
        siguiente_id = 1
        logger.warning("No se pudo cargar el archivo JSON.")


def guardar_libros():
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)

    archivo_temporal = ARCHIVO_LIBROS.with_suffix(".tmp")

    with archivo_temporal.open("w", encoding="utf-8") as archivo:
        json.dump(libros, archivo, ensure_ascii=False, indent=4)

    archivo_temporal.replace(ARCHIVO_LIBROS)
    logger.info("Libros guardados correctamente.")


def buscar_libro_por_id(libro_id: int):
    for libro in libros:
        if libro["id"] == libro_id:
            return libro

    raise HTTPException(
        status_code=404,
        detail="Libro no encontrado"
    )


cargar_libros()

@app.get("/")
def inicio():
    return {"API MI BIBLIOTECA"}








