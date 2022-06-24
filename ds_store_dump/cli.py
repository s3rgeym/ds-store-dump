import sys
from pathlib import Path

import click

from .DSStoreDumper import DSStoreDumper
from .log import logger
from .utils.decorators import async_run


# TODO: попробовать typer
@click.command()
@click.argument('urls', nargs=-1)
@click.option('-w', '--num_workers', default=10, help="Number of workers")
@click.option(
    '-o',
    '--output_directory',
    '--output',
    type=click.Path(file_okay=False, path_type=Path),
    default='output',
    help="Output directory",
)
@click.option(
    '-O',
    '--override',
    default=False,
    is_flag=True,
    help="Override existing files",
)
@click.option('-t', '--timeout', type=float, default=5.0, help="Client timeout")
@click.option(
    '-A',
    '--user_agent',
    '--agent',
    default="Mozilla/5.0",
    help="Client User-Agent string",
)
@click.option(
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
    log_levels = ['WARNING', 'INFO', 'DEBUG']
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
