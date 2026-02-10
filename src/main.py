from time import perf_counter

from arguments import parse_arguments
from exceptions import ApplicationException, unexpected_error
from logger import Logger
from output_parser import OutputParser
import text_style


def main() -> None:
    # parse the arguments in the script call
    arguments = parse_arguments()
    output_file = arguments.get_output_file()

    # parse the output file
    parser = OutputParser()
    t0 = perf_counter()
    try:
        with open(output_file, "r", encoding="utf-8") as file:
            for line in file:
                parser.feed(line)
    except StopIteration:
        pass
    t1 = perf_counter()
    delta_time = round((t1 - t0) * 1000, 1)
    Logger.debug(f"{text_style.DARK}{f" Output parsing done in {delta_time} ms ":~^80}{text_style.NONE}")

    # create the output obj and parse the arguments
    output_obj = parser.build()
    for arg in arguments.args:
        output_obj.parse_argument(arg)


if __name__ == '__main__':
    print(f"{text_style.BOLD}{text_style.CYAN}[ C23 BASIS SET COUNTER ]{text_style.NONE}")
    
    try:
        main()
    except ApplicationException as error:
        Logger.error(str(error))
    except Exception as error:
        unexpected_error(error)
    finally:
        print(f"{text_style.BOLD}{text_style.CYAN}[ FINISHED ]{text_style.NONE}")
