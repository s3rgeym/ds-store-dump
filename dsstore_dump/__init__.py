import asyncio
import os
import typing
from contextlib import asynccontextmanager
from dataclasses import dataclass
from urllib.parse import urljoin

import aiohttp
import click

from .utils.color_log import ColorLogger
from .utils.decorators import async_run

logger = ColorLogger(__name__)

DS_STORE_FILE = '.DS_Store'


def normalize_url(url: str) -> str:
    return url if '://' in url else f'http://{url}'


@dataclass
class DSStoreDumper:
    num_workers: int
    user_agent: str
    timeout: float

    @asynccontextmanager
    async def get_session(self) -> typing.AsyncIterable[aiohttp.ClientSession]:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            session.headers.setdefault("User-Agent", self.user_agent)
            yield session

    async def run(self, urls: typing.Sequence) -> None:
        queue = asyncio.Queue()
        for url in urls:
            url = normalize_url(url)
            url = urljoin(url, DS_STORE_FILE)
            queue.put_nowait(url)


# TODO: попробовать typer
@click.command()
@click.argument('urls', nargs=-1)
@click.option('-w', '--num_workers', default=10, help="Number of workers")
@click.option(
    '-A', '--user_agent', default="Mozilla/5.0", help="Client User-Agent string"
)
@click.option('-t', '--timeout', type=float, default=5.0, help="Client timeout")
@click.option(
    '-v', '--verbose', count=True, default=0, help="Be more verbosity"
)
@async_run
async def cli(
    urls: list[str],
    num_workers: int,
    user_agent: str,
    timeout: float,
    verbose: int,
) -> None:
    log_levels = ['WARNING', 'INFO', 'DEBUG']
    level = log_levels[min(verbose, len(log_levels) - 1)]
    logger.setLevel(level=level)
    dumper = DSStoreDumper(
        num_workers=num_workers,
        user_agent=user_agent,
        timeout=timeout,
    )
    await dumper.run(urls)
