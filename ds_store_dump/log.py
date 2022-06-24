import logging

from .utils.logging import ColoredFormatter

logger = logging.getLogger(__name__)
console = logging.StreamHandler()

# При форматировании цвета используются только при выводе в консоль
formatter = (
    ColoredFormatter if console.stream.isatty() else logging.Formatter
)("%(levelname)-8s | %(message)s")

console.setFormatter(formatter)
logger.addHandler(console)
