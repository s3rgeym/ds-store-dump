import sys
from functools import partial
from pathlib import Path

import click

from .DSStoreDumper import DSStoreDumper
from .log import logger
from .utils.decorators import async_run

click_option = partial(click.option, show_default=True)


# TODO: попробовать typer
@click.command()
@click.argument('urls', nargs=-1)
@click_option(
    '-w',
    '--num_workers',
    default=DSStoreDumper.num_workers,
    help="Number of workers",
)
@click_option(
    '-o',
    '--output_directory',
    '--output',
    type=click.Path(file_okay=False, path_type=Path),
    default=DSStoreDumper.output_directory,
    help="Output directory",
)
@click_option(
    '-O',
    '--override',
    default=DSStoreDumper.override,
    is_flag=True,
    help="Override existing files",
)
@click_option(
    '-t',
    '--timeout',
    type=float,
    default=DSStoreDumper.timeout,
    help="Client timeout",
)
@click_option(
    '-A',
    '--user_agent',
    '--agent',
    default=DSStoreDumper.user_agent,
    help="Client User-Agent",
)
@click_option(
    '-v', '--verbose', count=True, default=0, help="Be more verbosity"
)
@async_run
async def cli(
    urls: tuple[str, ...],
    num_workers: int,
    output_directory: Path,
    override: bool,
    timeout: float,
    user_agent: str,
    verbose: int,
) -> None:
    log_levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
    level = log_levels[min(verbose, len(log_levels) - 1)]
    logger.setLevel(level=level)
    urls = list(urls)
    if not urls:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                break
            urls.append(line)
    dumper = DSStoreDumper(
        num_workers=num_workers,
        output_directory=output_directory,
        override=override,
        timeout=timeout,
        user_agent=user_agent,
    )
    try:
        await dumper.run(urls)
    except Exception as e:
        logger.critical(e)
