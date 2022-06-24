import asyncio
import dataclasses
import re
import typing
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import unquote, urljoin

import aiohttp
from ds_store import DSStore, DSStoreEntry, buddy

from .log import logger

DOWNLOAD_RE = re.compile(
    '\.DS_Store|'
    '.*\.(?i)(?:tar|tgz|zip|rar|sql|env|ya?ml|json|co?nf|config|ini|inc|sh|bash|zsh|py3?|bak|swp|dockerfile|txt|docx?|md)'
)


def normalize_ds_store_url(url: str) -> str:
    if '://' not in url:
        url = f'http://{url}'
    if not url.endswith(f'/.DS_Store'):
        if not url.endswith('/'):
            url += '/'
        url = urljoin(url, '.DS_Store')
    return url


@dataclasses.dataclass
class DSStoreDumper:
    _: dataclasses.KW_ONLY
    num_workers: int
    output_directory: Path
    override: bool
    timeout: float
    user_agent: str

    @asynccontextmanager
    async def get_session(self) -> typing.AsyncIterable[aiohttp.ClientSession]:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            session.headers.setdefault('User-Agent', self.user_agent)
            yield session

    async def worker(
        self, download_queue: asyncio.Queue, seen_urls: set[str]
    ) -> None:
        async with self.get_session() as session:
            while True:
                try:
                    url = await download_queue.get()
                    if url is None:
                        break
                    logger.debug("url: %s", url)
                    if url in seen_urls:
                        logger.debug("skip seen: %s", url)
                        continue
                    seen_urls.add(url)
                    downloaded = self.output_directory / unquote(
                        url.split('://')[1]
                    )
                    if not downloaded.exists() or self.override:
                        try:
                            response: aiohttp.ClientResponse
                            async with session.get(url) as response:
                                response.raise_for_status()
                                downloaded.parent.mkdir(
                                    exist_ok=True, parents=True
                                )
                                with downloaded.open('wb') as fp:
                                    async for chunk in response.content.iter_chunked(
                                        8192
                                    ):
                                        fp.write(chunk)
                            logger.info("downloaded: %s", url)
                        except aiohttp.ClientResponseError as e:
                            logger.warn("%s: %s", e.status, url)
                            continue
                    if downloaded.name != '.DS_Store':
                        continue
                    logger.debug("parse: %s", downloaded)
                    with downloaded.open('rb') as fp:
                        try:
                            # TODO: разобраться как определить тип файла
                            # https://wiki.mozilla.org/DS_Store_File_Format
                            found_files = set(
                                entry.filename for entry in DSStore.open(fp)
                            )
                            for filename in found_files:
                                logger.debug("found: %s", filename)
                                file_url = urljoin(url, filename)
                                print(file_url)
                                if DOWNLOAD_RE.fullmatch(filename):
                                    await download_queue.put(file_url)
                                    continue
                                # Каталог?
                                if '.' not in filename:
                                    # Проверим есть ли в нем .DS_Store
                                    await download_queue.put(
                                        normalize_ds_store_url(file_url)
                                    )
                        except buddy.BuddyError:
                            logger.error("invalid file format: %s", downloaded)
                            downloaded.unlink()
                except Exception as e:
                    logger.error("An unexpected error: %s", e)
                finally:
                    download_queue.task_done()

    async def run(self, urls: typing.Sequence) -> None:
        download_queue = asyncio.Queue()
        seen_urls = set()
        for url in urls:
            url = normalize_ds_store_url(url)
            download_queue.put_nowait(url)
        worker_tasks = [
            asyncio.create_task(self.worker(download_queue, seen_urls))
            for _ in range(self.num_workers)
        ]
        await download_queue.join()
        for _ in range(self.num_workers):
            download_queue.put_nowait(None)
        for t in worker_tasks:
            await t
