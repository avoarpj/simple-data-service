"""
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.paths import BASE_DIR
from core.dataset_loader.loader import get_datasets
from core.dataset_meta.dataset import DatasetMeta
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Avoar SDS",
    description="O Simple Data Service é a fonte oficial da maioria dos dados do Avoar.<br>Aqui estão disponíveis snapshots e dumps completos de dados disponíveis somente para consulta sob demanda em formatos universais.",

    docs_url="/docs"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["paths"]["/public/datasets/centroides-municipios-brasileiros/centroides.json"] = {
        "get": {
            "tags": ["Centróide dos municípios brasileiros"],
            "summary": "Formato JSON",
            "description": "Este dataset contém o centróide dos municípios brasileiros, extraídos diretamente da malha digital oferecida pelo IBGE.",
            "responses": {
                "200": {
                    "description": "Centróides",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "codigo_municipio": {
                                            "type": "string",
                                            "description": "Código IBGE do município"
                                        },
                                        "nome_municipio": {
                                            "type": "string",
                                        },
                                        "uf": {
                                            "type": "string"
                                        },
                                        "latitude": {
                                            "type": "number"
                                        },
                                        "longitude": {
                                            "type": "number"
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            },
        }
    }

    openapi_schema["paths"]["/public/datasets/centroides-municipios-brasileiros/centroides.xml"] = {
        "get": {
            "tags": ["Centróide dos municípios brasileiros"],
            "summary": "Formato XML",
            "description": "Este dataset contém o centróide dos municípios brasileiros, extraídos diretamente da malha digital oferecida pelo IBGE.",
            "responses": {
                "200": {
                    "description": "Centróides",
                    "content": {
                        "text/xml": {
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "codigo_municipio": {
                                            "type": "string",
                                            "description": "Código IBGE do município"
                                        },
                                        "nome_municipio": {
                                            "type": "string",
                                        },
                                        "uf": {
                                            "type": "string"
                                        },
                                        "latitude": {
                                            "type": "number"
                                        },
                                        "longitude": {
                                            "type": "number"
                                        },
                                    },
                                    "xml": {
                                        "name": "municipio"
                                    }
                                },
                                "xml": {
                                    "name": "centroides",
                                    "wrapped": True
                                },
                            }
                        }
                    }
                }
            },
        }
    }

    openapi_schema["paths"]["/public/datasets/centroides-municipios-brasileiros/centroides.csv"] = {
        "get": {
            "tags": ["Centróide dos municípios brasileiros"],
            "summary": "Formato CSV",
            "description": "Este dataset contém o centróide dos municípios brasileiros, extraídos diretamente da malha digital oferecida pelo IBGE.",
            "responses": {
                "200": {
                    "description": "Centróides",
                    "content": {
                        "text/csv": {
                            "schema": {
                                "type": "string"
                            }
                        }
                    }
                }
            },
        }
    }

    openapi_schema["paths"]["/public/datasets/historico_deputados_federais/historico.json"] = {
        "get": {
            "tags": ["Histórico dos Deputados Federais (dump)"],
            "summary": "Formato JSON",
            "description": "Este dataset é um \"dump\" dos dados de histórico de cada deputado federal na Câmara dos Deputados, reunidos em um único arquivo json. <br>A API da Câmara (https://dadosabertos.camara.leg.br) já disponibiliza esses mesmos dados em API Rest, mas não um dump direto desses dados, o que dificulta a ingestão em massa.<br>O que esse dataset faz é basicamente facilitar isso ao fazer a parte suja de obter o histórico um por um na API e reunir em um arquivo para download, sem fazer nenhuma alteração nos dados originais.",
            "responses": {
                "200": {
                    "description": "",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "dados": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "number"
                                                },
                                                "uri": {
                                                    "type": "string"
                                                },
                                                "nome": {
                                                    "type": "string"
                                                },
                                                "nomeEleitoral": {
                                                    "type": "string"
                                                },
                                                "siglaPartido": {
                                                    "type": "string"
                                                },
                                                "uriPartido": {
                                                    "type": "string"
                                                },
                                                "siglaUf": {
                                                    "type": "string"
                                                },
                                                "idLegislatura": {
                                                    "type": "number"
                                                },
                                                "email": {
                                                    "type": "string"
                                                },
                                                "urlFoto": {
                                                    "type": "string"
                                                },
                                                "dataHora": {
                                                    "type": "string"
                                                },
                                                "situacao": {
                                                    "type": "string"
                                                },
                                                "condicaoEleitoral": {
                                                    "type": "string"
                                                },
                                                "descricaoStatus": {
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

public_path = BASE_DIR / "public"

app.mount(
    "/public",
    StaticFiles(directory=public_path),
)

@app.get(
    "/datasets",
    name="",
    description="Este endpoint lista a configuração de todos os datasets gerados pelo SDS.",
    status_code=200,
    response_model=list[DatasetMeta],
    tags=["Todos os datasets"]
)
async def datasets():
    data = get_datasets()
    return data 

app.openapi = custom_openapi