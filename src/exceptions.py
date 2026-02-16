from pathlib import Path
import traceback

from text_style import TextStyle


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
        lines.append(f'File {TextStyle.YELLOW}"{filename}"{TextStyle.NONE}, line {TextStyle.YELLOW}{frame.lineno}{TextStyle.NONE}, in {TextStyle.YELLOW}{frame.name}{TextStyle.NONE}')
        if frame.line:
            lines.append(f"  {TextStyle.RED}{frame.line.strip()}{TextStyle.NONE}")

    exception_name = type(exception).__name__
    lines.append(f"{TextStyle.BOLD + TextStyle.PURPLE}{exception_name}{TextStyle.NONE}{TextStyle.PURPLE}: {exception}{TextStyle.NONE}")

    return "\n".join(lines)

def unexpected_error(exception: BaseException) -> None:
    print(f"{TextStyle.BOLD + TextStyle.RED}[ UNEXPECTED ERROR - PROGRAM STOPPED ]{TextStyle.NONE}")
    print(f"{" Traceback (most recent call last) ":=^80}")
    print(format_traceback(exception))
    print("=" * 80)