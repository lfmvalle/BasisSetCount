from pathlib import Path
from typing import Optional
from exceptions import ParsingException
from dataclasses import dataclass
import re
import sys
from time import perf_counter

import regex_pattern
import text_style
from logger import Logger


@dataclass
class Argument:
    value: str

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"


class FileArgument(Argument):
    ...


class NumberArgument(Argument):
    ...


class RangeArgument(Argument):
    ...


class ParameterArgument(Argument):
    ...


class ArgumentParser:
    valid_parameters = ["-a", "-b", "x"]

    @staticmethod
    def is_file(arg: str) -> bool:
        if not arg: return False
        
        path = Path(arg)
        if not path.exists(): return False
        if not path.is_file(): return False
        return True

    @staticmethod
    def is_number(arg: str) -> bool:
        if not re.findall(regex_pattern.NUMBER_ARG_REGEX, arg):
            return False
        return True

    @staticmethod
    def is_range(arg: str) -> bool:
        if not re.findall(regex_pattern.RANGE_ARG_REGEX, arg):
            return False
        return True

    @classmethod
    def is_parameter(cls, arg: str) -> bool:
        if arg not in cls.valid_parameters:
            return False
        return True

    @staticmethod
    def parse(arg: str) -> Optional[Argument]:
        PARSER_MAP = {
            ArgumentParser.is_file: FileArgument,
            ArgumentParser.is_number: NumberArgument,
            ArgumentParser.is_range: RangeArgument,
            ArgumentParser.is_parameter: ParameterArgument
        }
        for check, cls in PARSER_MAP.items():
            if check(arg): return cls(arg)


class ArgumentHandler:
    def __init__(self, args: list[str]):
        t0 = perf_counter()
        self.args: list[Argument] = []
        self._file: Optional[FileArgument] = None

        if "-debug" in args:
            args.remove("-debug")
            if not Logger.debugging:
                    Logger.debugging = True
                    Logger.info("Debug mode is now active")
        
        for arg in args:
            Logger.debug(f"Parsing: {text_style.PURPLE}{arg}{text_style.NONE}")
            parsed = ArgumentParser.parse(arg)
            
            if not parsed:
                Logger.warn(f"Ignoring invalid argument: {text_style.BOLDITALIC}{arg}{text_style.NONE}")
                continue

            self._register_arg(parsed)
        t1 = perf_counter()
        delta_time = round((t1 - t0) * 1000, 1)
        Logger.debug(f"{text_style.DARK}{f" Argument parsing done in {delta_time} ms ":~^80}{text_style.NONE}")
    
    def _register_arg(self, arg: Argument) -> None:
        if isinstance(arg, FileArgument):
            if self._file:
                raise ParsingException("Only one file must be provided in the script call.")
            self._file = arg
        else:
            if arg in self.args:
                Logger.warn(f"Ignoring duplicated argument: {text_style.BOLDITALIC}{arg.value}{text_style.NONE}")
            else:
                self.args.append(arg)
        
        Logger.debug(f"Done: {text_style.PURPLE}{repr(arg)}{text_style.NONE}")
    
    def get_output_file(self) -> Path:
        if not self._file:
            raise ParsingException(f"A {text_style.BOLD}CRYSTAL output file{text_style.NONE} must be provided.")
        return Path(self._file.value)
    
    @property
    def parameters(self) -> list[ParameterArgument]:
        return [arg for arg in self.args if isinstance(arg, ParameterArgument)]
    
    @property
    def numbers(self) -> list[NumberArgument]:
        return [arg for arg in self.args if isinstance(arg, NumberArgument)]
    
    @property
    def ranges(self) -> list[RangeArgument]:
        return [arg for arg in self.args if isinstance(arg, RangeArgument)]


def parse_arguments() -> ArgumentHandler:
    if not len(sys.argv) > 1:
        raise ParsingException(f"Invalid number of arguments on script call. A {text_style.BOLD}CRYSTAL output file{text_style.NONE} must be provided.")
    
    return ArgumentHandler(sys.argv[1:])