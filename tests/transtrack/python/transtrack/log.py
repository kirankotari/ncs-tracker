"""
Application logging operations
"""

import logging
from functools import lru_cache


class SingletonMeta(type):
    __call__ = lru_cache(maxsize=None)(type.__call__)


class Logger(metaclass=SingletonMeta):
    """
    Logger with singleton metaclass
    """
    level = logging.DEBUG
    format = '%(levelname)-8s | %(asctime)s | %(pathname)-8s:%(lineno)-4d | %(message)s'
    log = logging.basicConfig(level=level, format=format) or logging.getLogger()

    def __init__(self, level=logging.INFO) -> None:
        self.log.setLevel(level)
        self.log.debug(f"log level changed to {level}")
