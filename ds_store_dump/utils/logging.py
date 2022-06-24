import logging

from .termcolors import Back, Fore, Style


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        message: str = super().format(record)
        if color := self.COLORS.get(record.levelname):
            message = color + message + Style.RESET
        return message
