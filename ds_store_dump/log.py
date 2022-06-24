import logging
import sys

from .utils.logging import ColoredFormatter

logger = logging.getLogger(__name__)
# При форматировании цвета используются только при выводе в консоль
formatter_class = ColoredFormatter if sys.stderr.isatty() else logging.Formatter
formatter = formatter_class("[%(levelname)s]: %(asctime)s - %(message)s")
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)
