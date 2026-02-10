from pathlib import Path
import traceback

import text_style


class ApplicationException(Exception): ...
class ParsingException(ApplicationException): ...
class OutputException(ApplicationException): ...
class GhostException(ApplicationException): ...
class PeriodicTableException(ApplicationException): ...


def format_traceback(exception: BaseException) -> str:
    tb = traceback.TracebackException.from_exception(exception)

    lines = []

    for frame in tb.stack:
        filename = Path(frame.filename).name  # avoid exposing user paths, cleaner output
        lines.append(f'File {text_style.YELLOW}"{filename}"{text_style.NONE}, line {text_style.YELLOW}{frame.lineno}{text_style.NONE}, in {text_style.YELLOW}{frame.name}{text_style.NONE}')
        if frame.line:
            lines.append(f"  {text_style.RED}{frame.line.strip()}{text_style.NONE}")

    exception_name = type(exception).__name__
    lines.append(f"{text_style.BOLD}{text_style.PURPLE}{exception_name}{text_style.NONE}{text_style.PURPLE}: {exception}{text_style.NONE}")

    return "\n".join(lines)

def unexpected_error(exception: BaseException) -> None:
    print(f"{text_style.BOLD}{text_style.RED}[ UNEXPECTED ERROR - PROGRAM STOPPED ]{text_style.NONE}")
    print(f"{" Traceback (most recent call last) ":=^80}")
    print(format_traceback(exception))
    print("=" * 80)