from enum import Enum

import text_style
from text_style import TextStyle


class LogLevel(Enum):
    INFO = 0,
    REQUEST = 1
    WARNING = 2,
    ERROR = 3
    DEBUG = 4,


class Logger:
    debugging = False

    @staticmethod
    def _log_message(level: LogLevel, message: str) -> None:
        log_string = f"{TextStyle.BOLD}"
        match level:
            case LogLevel.INFO:
                log_string += f"[ INFO ]{TextStyle.NONE} "
            case LogLevel.REQUEST:
                log_string += f"{TextStyle.GREEN}[ REQUEST ]{TextStyle.NONE} "
            case LogLevel.WARNING:
                log_string += f"{TextStyle.YELLOW}[ WARNING ]{TextStyle.NONE} "
            case LogLevel.ERROR:
                log_string += f"{TextStyle.RED}[ ERROR ]{TextStyle.NONE} "
            case LogLevel.DEBUG:
                log_string += f"{TextStyle.PURPLE}[ DEBUG ]{TextStyle.NONE} "
        log_string += message
        print(log_string)

    @classmethod
    def info(cls, message: str) -> None:
        return cls._log_message(LogLevel.INFO, message)
    
    @classmethod
    def request(cls, message: str) -> None:
        return cls._log_message(LogLevel.REQUEST, message)

    @classmethod
    def warn(cls, message: str) -> None:
        return cls._log_message(LogLevel.WARNING, message)

    @classmethod
    def error(cls, message: str) -> None:
        return cls._log_message(LogLevel.ERROR, message)

    @classmethod
    def debug(cls, message: str) -> None:
        if not cls.debugging: return
        return cls._log_message(LogLevel.DEBUG, message)