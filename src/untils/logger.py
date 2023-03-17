from __future__ import annotations
import asyncio
from datetime import datetime
import inspect
import os
import traceback
from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class LogTypes(str, Enum):
    info = 'info'
    error = 'error'
    debug = 'debug'
    warning = 'warning'


class Log:
    def __init__(self, text: str, log_type: LogTypes = LogTypes.info, tag: str | None = None):
        self._text = text
        self._tag = tag
        self._log_type = log_type

    @property
    def text(self) -> str:
        return self._text

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def log_type(self) -> LogTypes:
        return self._log_type


class Logger(ABC):
    def __init__(self, tags=None):
        if tags is None:
            tags = []
        self._tags = tags

    @property
    def tags(self) -> List[str]:
        return self._tags

    async def _format(self, log: Log, is_color: bool = False, is_html: bool = False) -> str:
        frame = inspect.currentframe()
        filename = inspect.getframeinfo(frame).filename
        rel_path = os.path.relpath(filename)

        stack = traceback.extract_stack(limit=3)[0]
        description = f'{datetime.now().strftime("%m.%d.%Y %H:%M:%S")} [{log.log_type.value.title()}] {rel_path}:{stack.lineno} -'
        text = log.text

        if is_html:
            description = f'<b>{description}</b>'
            text = f'<code>{text}</code>'
        if is_color:
            match log.log_type:
                case LogTypes.info:
                    description = f'\033[1;36m{description}\033[m'

                case LogTypes.error:
                    description = f'\033[1;33;91m{description}\033[m'

                case LogTypes.debug:
                    description = f'\033[1;32m{description}\033[m'

                case LogTypes.warning:
                    description = f'\033[1;31m{description}\033[m'

        return f'{description} {text}'

    @abstractmethod
    async def log(self, log: Log):
        pass


class LoggerGroup:
    def __init__(self, loggers: List[Logger]):
        self._logger = loggers

    async def log(self, log: Log):
        for logger in self._logger:
            await logger.log(log)


class FileLogger(Logger):
    async def log(self, log: Log):
        pass


class ConsoleLogger(Logger):
    async def log(self, log: Log):
        if log.tag not in self.tags and self.tags:
            return
        await asyncio.to_thread(print, await self._format(log, is_color=True))
