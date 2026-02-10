from pathlib import Path

from arguments import *
from atom import Atom
from basis_set import BasisSet, FunctionType, AtomicFunctions
from logger import Logger
import text_style


class CrystalOutput:
    def __init__(self, atoms: list[Atom], basis_sets: list[BasisSet]) -> None:
        self.atoms = atoms
        self.basis_sets = basis_sets
    
    def _atoms_info(self) -> None:
        Logger.info("Atoms in the output file (coordinates from basis set section):")
        print("\n", "-" * 67, sep="")
        print(f"{text_style.BOLD}{"Label":^8s}{"Element":^10s}{"X":^8s}{"Y":^8s}{"Z":^8s}{"Atomic functions range":^25}{text_style.NONE}")
        print("-" * 67)
        c = 0
        local_count = 0
        last_count = 0
        for atom in self.atoms:
            if atom.basis_set is not None:
                for basis_function in atom.basis_set.basis_functions:
                    local_count += basis_function.function_type.value
            c += 1
            color = text_style.NONE
            if c % 2 != 0: color = text_style.DARK
            if atom.is_ghost: color += text_style.PURPLE
            
            element_str = f"Xx ({atom.element.symbol})" if atom.is_ghost else atom.element.symbol
            print(f"{color}{atom.label:^8d}{element_str:^10s}{atom.x:^ 8.3f}{atom.y:^ 8.3f}{atom.z:^ 8.3f}{f"{last_count + 1: d}-{local_count}":^25s}{text_style.NONE}")
            last_count = local_count
        print("-" * 67, "\n", sep="")

    def _basis_sets_info(self) -> None:
        Logger.info("Basis sets in the output file:")
        print()
        for basis_set in self.basis_sets:
            label_count = 0
            basis_function_count = 0
            primitive_count = 0
            for atom in self.atoms:
                if atom.basis_set == basis_set:
                    label_count += 1
            print(f"{f"{text_style.PURPLE}{basis_set.element.symbol} (Z = {basis_set.element.atomic_number}){text_style.NONE}":^40s}{f"Used by {text_style.PURPLE}{label_count} atoms{text_style.NONE}":>40s}")
            print("-" * 80)
            print(f"{text_style.BOLD}{"Atomic function":^16s}{"Exponent":^16s}{"s coeff.":^16s}{"p coeff.":^16s}{"d/f/g coeff.":^16s}{text_style.NONE}")
            print("-" * 80)
            for basis_function in basis_set.basis_functions:
                basis_function_count += 1
                print(f"{basis_function.function_type.name:^16s}")
                for primitive in basis_function.primitives:
                    primitive_count += 1
                    print(f"{"":^16s}{primitive.exponent:^ 16.3E}{primitive.s_coeff:^ 16.3E}{primitive.p_coeff:^ 16.3E}{primitive.dfg_coeff:^16.3E}")
            print("-" * 80)
            print(f"{f"Total: {text_style.PURPLE}{basis_function_count}{text_style.NONE} basis functions | {text_style.PURPLE}{primitive_count}{text_style.NONE} primitives":>80s}\n")

    def _parse_ghost_atoms(self) -> None:
        Logger.info("Ghost atoms:")
        for atom in self.atoms:
            if atom.is_ghost:
                self._parse_atom(atom.label)

    @staticmethod
    def _print_atomic_function(index: int, function: str) -> None:
        print(f"{"":16s}{index:^16d}{function:<16s}")

    def _count_atom(self, sum: int, atom: Atom) -> None:
        if atom.basis_set is None:
            return
    
        FUNCTION_MAP = {
            FunctionType.S: AtomicFunctions.S.value,
            FunctionType.SP: AtomicFunctions.SP.value,
            FunctionType.P: AtomicFunctions.P.value,
            FunctionType.D: AtomicFunctions.D.value,
            FunctionType.F: AtomicFunctions.F.value,
            FunctionType.G: AtomicFunctions.G.value,
        }

        print("-" * 48)
        print(f"{text_style.BOLD}{"Atomic function":^16s}{"Index":^16s}{"Atomic orbital":<16s}{text_style.NONE}")
        print("-" * 48)
        for basis_function in atom.basis_set.basis_functions:
            print(f"{basis_function.function_type.name:^16s}")
            for function in FUNCTION_MAP[basis_function.function_type]:
                sum += 1
                self._print_atomic_function(sum, function)
        print("-" * 48)
    
    def _parse_atom(self, label: int) -> None:
        local_count = 0
        print()
        for atom in self.atoms:
            if atom.basis_set is not None:
                # found the atom: print
                if atom.label == label:
                    this_count = local_count
                    for basis_function in atom.basis_set.basis_functions:
                        this_count += basis_function.function_type.value
                    if atom.is_ghost:
                        print(f"Local atomic functions of {text_style.PURPLE}Atom {atom.label} - Xx ({atom.element.symbol}){text_style.NONE}")
                    else:
                        print(f"Local atomic functions of {text_style.PURPLE}Atom {atom.label} - {atom.element.symbol}{text_style.NONE}")
                    self._count_atom(local_count, atom)
                    break
                else:
                    for basis_function in atom.basis_set.basis_functions:
                        local_count += basis_function.function_type.value

    def _parse_number_argument(self, arg: NumberArgument) -> None:
        Logger.debug(f"Parsing number argument: {text_style.PURPLE}{arg.value}{text_style.NONE}")
        Logger.info(f"Enumeration for {text_style.PURPLE}Atom {arg.value}{text_style.NONE}:")
        return self._parse_atom(int(arg.value))
    
    def _parse_range_argument(self, arg: RangeArgument) -> None:
        Logger.debug(f"Parsing range argument: {text_style.PURPLE}{arg.value}{text_style.NONE}")
        Logger.info(f"Enumeration for {text_style.PURPLE}Atoms {arg.value}{text_style.NONE}:")
        limits = arg.value.split("-")
        x, y = int(limits[0]), int(limits[1]) + 1
        if x > y:
            for i in range(x, y - 2, -1):
                self._parse_atom(i)
        else:
            for i in range(x, y):
                self._parse_atom(i)

    def _parse_parameter_argument(self, arg: ParameterArgument) -> None:
        Logger.debug(f"Parsing parameter argument: {text_style.PURPLE}{arg.value}{text_style.NONE}")
        if arg.value == "-a":
            return self._atoms_info()
        elif arg.value == "-b":
            return self._basis_sets_info()
        elif arg.value == "x":
            return self._parse_ghost_atoms()

    def parse_argument(self, arg: Argument) -> None:
        PARSE_MAP = {
            NumberArgument: self._parse_number_argument,
            RangeArgument: self._parse_range_argument,
            ParameterArgument: self._parse_parameter_argument
        }

        return PARSE_MAP[type(arg)](arg)