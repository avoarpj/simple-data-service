"""
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.paths import BASE_DIR
from core.dataset_loader.loader import get_datasets
from core.dataset_meta.dataset import DatasetMeta


app = FastAPI(
    title="Avoar SDS",
    description="Simple Data Service é um serviço responsável por montar e servir datasets para o projeto Avoar. Ele é responsável por gerar conjuntos nos 3 principais formatos da web (csv, json e xml) derviados de dados mais complexos, como a malha digital do território brasileiro.",

    redoc_url="/docs",
    docs_url=None,
)

public_path = BASE_DIR / "public"

app.mount(
    "/public",
    StaticFiles(directory=public_path),
)

@app.get(
    "/datasets",
    name="Todos os datasets",
    description="Este endpoint lista a configuração de todos os datasets gerados pelo SDS.",
    status_code=200,
    response_model=list[DatasetMeta]
)
async def datasets():
    data = get_datasets()
    return data 