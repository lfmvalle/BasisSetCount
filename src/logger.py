from enum import Enum

import text_style


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
        log_string = f"[bold]"
        match level:
            case LogLevel.INFO:
                log_string += f"[ INFO ][/] "
            case LogLevel.REQUEST:
                log_string += f"[green][ REQUEST ][/] "
            case LogLevel.WARNING:
                log_string += f"[yellow][ WARNING ][/] "
            case LogLevel.ERROR:
                log_string += f"[red][ ERROR ][/] "
            case LogLevel.DEBUG:
                log_string += f"[purple][ DEBUG ][/] "
        log_string += message
        log = text_style.parse_styles(log_string)
        print(log)

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