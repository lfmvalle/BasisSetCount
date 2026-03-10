#!/usr/bin/env python3

from time import perf_counter

from arguments import parse_arguments
from bootstrap import init_resources
from exceptions import ApplicationException, unexpected_error
from logger import Logger
from output_parser import OutputParser
from printer import Printer
from text_style import printf


def main() -> None:
    # initialize resources
    init_resources()

    # parse the arguments in the script call
    arguments = parse_arguments()
    output_file = arguments.get_output_file()

    # parse the output file
    parser = OutputParser()
    t0 = perf_counter()
    try:
        with open(output_file, "r", encoding="utf-8") as file:
            for line in file:
                parser.feed(line.strip("\n"))
    except StopIteration:
        pass
    t1 = perf_counter()
    delta_time = round((t1 - t0) * 1000, 1)
    Logger.debug(f"[dim]{f" Output parsing done in {delta_time} ms ":~^80}[/]")

    # create the output obj and parse the arguments
    t0 = perf_counter()
    output_obj = parser.build()
    t1 = perf_counter()
    delta_time = round((t1 - t0) * 1000, 1)
    Logger.debug(f"[dim]{f" Output object builded in {delta_time} ms ":~^80}[/]")
    
    # Parse arguments and print requests
    printer = Printer(output_obj)
    for arg in arguments.args:
        tables = printer.parse_argument(arg)
        for table in tables:
            print(table)

if __name__ == '__main__':
    printf("[bold cyan][ C23 BASIS SET COUNTER ][/]")
    
    try:
        main()
    except ApplicationException as error:
        Logger.error(str(error))
    except Exception as error:
        unexpected_error(error)
    finally:
        printf(f"[bold cyan][ FINISHED ][/]")
