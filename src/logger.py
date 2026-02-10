from enum import Enum

import text_style


class LogLevel(Enum):
    INFO = 0,
    WARNING = 1,
    ERROR = 2
    DEBUG = 3,


class Logger:
    debugging = False

    @staticmethod
    def _log_message(level: LogLevel, message: str) -> None:
        log_string = ""
        match level:
            case LogLevel.INFO:
                log_string += f"{text_style.BOLD}[ INFO ]{text_style.NONE} "
            case LogLevel.WARNING:
                log_string += f"{text_style.BOLD}{text_style.YELLOW}[ WARNING ]{text_style.NONE} "
            case LogLevel.ERROR:
                log_string += f"{text_style.BOLD}{text_style.RED}[ ERROR ]{text_style.NONE} "
            case LogLevel.DEBUG:
                log_string += f"{text_style.BOLD}{text_style.PURPLE}[ DEBUG ]{text_style.NONE} "
        log_string += message
        print(log_string)

    @classmethod
    def info(cls, message: str) -> None:
        return cls._log_message(LogLevel.INFO, message)

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