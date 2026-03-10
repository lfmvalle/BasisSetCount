from pathlib import Path
import traceback

from text_style import printf

class ApplicationException(Exception): ...
class ParsingException(ApplicationException): ...
class OutputException(ApplicationException): ...
class GhostException(ApplicationException): ...
class PeriodicTableException(ApplicationException): ...
class CellException(ApplicationException): ...
class TableException(ApplicationException): ...


def format_traceback(exception: BaseException) -> str:
    tb = traceback.TracebackException.from_exception(exception)

    lines = []

    for frame in tb.stack:
        filename = Path(frame.filename).name  # avoid exposing user paths, cleaner output
        lines.append(f'File [yellow]"{filename}"[/], line [yellow]{frame.lineno}[/], in [yellow]{frame.name}[/]')
        if frame.line:
            lines.append(f"  [red]{frame.line.strip()}[/]")

    exception_name = type(exception).__name__
    lines.append(f"[bold purple]{exception_name}[/ purple]: {exception}[/]")

    return "\n".join(lines)

def unexpected_error(exception: BaseException) -> None:
    printf(f"[bold red][ UNEXPECTED ERROR - PROGRAM STOPPED ][/]")
    printf(f"{" Traceback (most recent call last) ":=^80}")
    printf(format_traceback(exception))
    printf("=" * 80)