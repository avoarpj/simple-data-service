import asyncio
import aiohttp
import time
import random
from pathlib import Path
from pydantic import BaseModel


class Item(BaseModel):
    url: str
    path: Path


class BulkDownloader:
    def __init__(
        self,
        rate: int,
        concurrency: int = 5,
        callback=None,
        retry_base_delay: int = 1,
        retry_max_delay: int = 3600,
        timeout_kwargs: dict | None = None,
        connector_kwargs: dict | None = None,
        task_delay: float | None = None,
        task_jitter: float | None = None, 
    ):
        self.rate = rate
        self.interval = 1 / rate
        self.callback = callback

        self.sem = asyncio.Semaphore(concurrency)

        self._last = 0.0
        self._rate_lock = asyncio.Lock()

        self._session: aiohttp.ClientSession | None = None
        self._session_lock = asyncio.Lock()

        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay

        self._timeout_kwargs = timeout_kwargs or {}
        self._connector_kwargs = connector_kwargs or {}

        self.task_delay = task_delay
        self.task_jitter = task_jitter

        self._task_lock = asyncio.Lock()

    async def _rate_limit(self):
        async with self._rate_lock:
            now = time.monotonic()
            delta = now - self._last

            if delta < self.interval:
                await asyncio.sleep(self.interval - delta)

            self._last = time.monotonic()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session and not self._session.closed:
            return self._session

        async with self._session_lock:
            if self._session and not self._session.closed:
                return self._session

            timeout = aiohttp.ClientTimeout(**self._timeout_kwargs)
            connector = aiohttp.TCPConnector(**self._connector_kwargs)

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
            return self._session

    async def _stagger(self):
        if self.task_delay is None:
            return

        delay = self.task_delay
        if self.task_jitter:
            delay += random.uniform(0, self.task_jitter)

        await asyncio.sleep(delay)

    async def _download_one(self, item: Item):
        attempt = 0

        await self._stagger() # evita o comportamento de rajada

        print(f"Downloading {item.url}")
        while True:
            try:
                async with self.sem:
                    await self._rate_limit()
                    session = await self._get_session()

                    item.path.parent.mkdir(parents=True, exist_ok=True)

                    headers = {
                        "User-Agent": "Avoar SDS (https://github.com/avoarpj/simple-data-service)"
                    }

                    async with session.get(item.url, headers=headers) as resp:
                        resp.raise_for_status()

                        with open(item.path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(8192):
                                f.write(chunk)

                if self.callback:
                    self.callback(item)

                return

            except asyncio.CancelledError:
                raise

            except Exception as e:
                delay = min(
                    self.retry_base_delay * (2 ** attempt),
                    self.retry_max_delay
                )

                delay *= 0.9 + (0.2 * random.random())
                attempt += 1

                print(
                    f"[retry] {item.url} → tentativa {attempt} será refeita com delay de {delay:.1f}s quando chegar novamente "
                    f"({type(e).__name__})"
                )

                await asyncio.sleep(delay)

    async def download_all(
        self,
        items: list[Item],
        timeout: float | None = None
    ):
        tasks = [asyncio.create_task(self._download_one(i)) for i in items]

        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)

        except asyncio.TimeoutError:
            for t in tasks:
                t.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

            raise TimeoutError(f"Bulk download exceeded timeout of {timeout}s")

        finally:
            if self._session and not self._session.closed:
                await self._session.close()