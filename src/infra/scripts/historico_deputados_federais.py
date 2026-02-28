from core.dataset_meta.dataset import DatasetMeta
from core.filetagger.filetag import write_filetag_meta, FiletagMeta
from infra.dataset_types.historico_deputados_federais.deputy import CD_DeputiesRaw
from infra.dataset_types.historico_deputados_federais.history import CD_HistoryRaw, CD_History
from infra.BulkDownloader import BulkDownloader, Item
from pathlib import Path
from core.paths import BASE_DIR
from datetime import datetime
import os

def _onDownload(item: Item):
    write_filetag_meta(
        path=item.path.parent / "ftag.json",
        meta=FiletagMeta(createdAt=datetime.now())
    )

_downloader = BulkDownloader(
    rate=2,
    concurrency=2,
    retry_base_delay=1,
    retry_max_delay=480,
    connector_kwargs=dict(
        limit=2,
        keepalive_timeout=4,
        ttl_dns_cache=300,
        force_close=False
    ),
    timeout_kwargs=dict(
        total=120,
        connect=30,
        sock_read=60
    ),
    task_delay=2.0,
    task_jitter=1.5,
    callback=_onDownload
)

async def Callback(dataset: DatasetMeta) -> None:
    dataset.downloadIfNecessary()
    fpath = dataset.getProcessFile()

    if fpath is None:
        raise FileNotFoundError(f"Cannot find process file")
    
    if dataset.output.path.jjson is None:
        raise FileNotFoundError(f"No json path provided")

    deputies_path = BASE_DIR / Path(fpath.path)

    with open(deputies_path, 'r') as f:
        json_data = f.read()

    deputies = CD_DeputiesRaw.model_validate_json(json_data=json_data)
    download_urls: list[Item] = []
    all_ids: list[str] = []

    for deputy in deputies.dados:
        id = deputy.get_id()
        folder = Path(fpath.path).parent / Path(id)
        file = folder / Path(f"{id}.json")
        ftag = folder / Path("ftag.json")

        all_ids.append(id)

        if not ftag.exists() or not file.exists():
            file.unlink(missing_ok=True)
            ftag.unlink(missing_ok=True)

            try:
                folder.rmdir()
            except:
                pass

            download_urls.append(Item(
                url=f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/historico",
                path=file
            ))

    await _downloader.download_all(download_urls, 86400)

    all_data: list[CD_History] = []

    for id in all_ids:
        folder = Path(fpath.path).parent / Path(id)
        file = folder / Path(f"{id}.json")

        with open(file, 'r') as f:
            contents = f.read()

        histories = CD_HistoryRaw.model_validate_json(contents)

        for history in histories.dados:
            all_data.append(history)

    full_data = CD_HistoryRaw(
        dados=all_data
    )

    json_str = full_data.model_dump_json(
        indent=4
    )

    (BASE_DIR / Path(dataset.output.path.jjson).parent).mkdir(parents=True, exist_ok=True)

    with open(f"{dataset.output.path.jjson}.temp", "w", encoding="utf-8") as f:
        f.write(json_str)

    os.replace(f"{dataset.output.path.jjson}.temp", dataset.output.path.jjson)

    return