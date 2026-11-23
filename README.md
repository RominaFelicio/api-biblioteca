# API-BIBLIOTECA

API REST para gestionar libros utilizando Python y FastAPI.

## Requisitos
- Python 3.10 o superior.
- pip para instalar las dependencias.

## Instalacion
1. Clonar o descargar este repositorio.
2. Crear y activar un entorno virtual.
3. Instalar las dependencias con `pip install -r requirements.txt`.

## Ejecutar la API
Desde la carpeta principal del proyecto, ejecutar:

`fastapi dev main.py`

Tambien se puede iniciar con:

`uvicorn main:app --reload`

## Documentacion interactiva
Con el servidor iniciado, abrir `http://127.0.0.1:8000/docs`.

## Persistencia
Los libros se guardan automaticamente en `datos/libros.json`.
El archivo y la carpeta se crean cuando se registra el primer libro.

## Endpoints principales
- `GET /` mensaje de bienvenida.
- `GET /libros` lista, filtros y paginacion.
- `GET /libros/buscar?texto=...` busca por titulo o autor.
- `POST /libros` crea un libro.
- `GET /libros/{id}` consulta un libro.
- `PUT /libros/{id}` reemplaza todos sus datos.
- `PATCH /libros/{id}` actualiza algunos datos.
- `DELETE /libros/{id}` elimina un libro.
