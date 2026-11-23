from pathlib import Path
import json
import logging

from opentelemetry.trace import Status
from pydantic import BaseModel, ConfigDict, Field
from fastapi import FastAPI, HTTPException, Query, status

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

# I9 - BUSCAR POR TEXTO

@app.get("/libros/buscar", response_model=list[Libro])
def buscar_libros(texto: str = Query(..., min_length=1)):
    texto = texto.strip().lower()

    resultados = [
        libro for libro in libros
        if texto in libro["titulo"].lower()
        or texto in libro["autor"].lower()
    ]

    return sorted(resultados, key=lambda libro: libro["id"])


# F2 - I3 - I4 LISTAR, FILTRAR Y PAGINAR

@app.get("/libros", response_model=list[Libro])
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1)
):
    resultado = sorted(libros, key=lambda libro: libro["id"])

    if autor is not None:
        resultado = [
            libro for libro in resultado
            if libro["autor"].lower() == autor.lower()
        ]

    if disponible is not None:
        resultado = [
            libro for libro in resultado
            if libro["disponible"] is disponible
        ]

    return resultado[desde:desde + limite]

# F3 - I1 - I6 CREAR LIBRO

@app.post(
    "/libros",
    response_model=Libro,
    status_code=status.HTTP_201_CREATED # type: ignore
)
def crear_libro(datos: LibroEntrada):
    global siguiente_id

    for libro in libros:
        if (
            libro["titulo"].lower() == datos.titulo.lower()
            and libro["autor"].lower() == datos.autor.lower()
        ):
            raise HTTPException(
                status_code=409,
                detail="Ya existe un libro con ese titulo y autor"
            )

    nuevo_libro = {
        "id": siguiente_id,
        "titulo": datos.titulo,
        "autor": datos.autor,
        "anio": datos.anio,
        "disponible": datos.disponible
    }

    libros.append(nuevo_libro)
    siguiente_id += 1

    libros.sort(key=lambda libro: libro["id"])
    guardar_libros()

    logger.info("Libro creado: %s", nuevo_libro["id"])

    return nuevo_libro


# F4 - F5 CONSULTAR POR ID

@app.get("/libros/{libro_id}", response_model=Libro)
def obtener_libro(libro_id: int):
    return buscar_libro_por_id(libro_id)


# I2 ACTUALIZAR COMPLETAMENTE (PUT)

@app.put("/libros/{libro_id}", response_model=Libro)
def reemplazar_libro(libro_id: int, datos: LibroEntrada):
    libro = buscar_libro_por_id(libro_id)

    libro["titulo"] = datos.titulo
    libro["autor"] = datos.autor
    libro["anio"] = datos.anio
    libro["disponible"] = datos.disponible

    guardar_libros()
    logger.info("Libro reemplazado: %s", libro_id)

    return libro


# I5 ACTUALIZAR PARCIALMENTE (PATCH)

@app.patch("/libros/{libro_id}", response_model=Libro)
def actualizar_libro(libro_id: int, datos: LibroActualizacion):
    libro = buscar_libro_por_id(libro_id)

    cambios = datos.model_dump(exclude_unset=True)

    if any(valor is None for valor in cambios.values()):
        raise HTTPException(
            status_code=422,
            detail="Los campos enviados no pueden ser null"
        )

    for campo, valor in cambios.items():
        libro[campo] = valor

    guardar_libros()
    logger.info("Libro actualizado: %s", libro_id)

    return libro


# F6 ELIMINAR LIBRO

@app.delete(
    "/libros/{libro_id}",
    status_code=status.HTTP_204_NO_CONTENT # type: ignore
)
def eliminar_libro(libro_id: int):
    libro = buscar_libro_por_id(libro_id)

    libros.remove(libro)
    guardar_libros()

    logger.info("Libro eliminado: %s", libro_id)

    






