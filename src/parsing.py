import re
from classes import *
from exceptions import *
from typing import Iterable


class CrystalOutput:
    """
    The ***Crystal Output*** class receives a CRYSTAL output file containing Basis Set information.

    Parameters
    ----------
    filepath: str
        The path to the output file.
    
    Attributes
    ----------
    atoms : list[Atom]
        *Atom* objects found in the output file.

    basis_sets: list[BasisSet]
        *Basis Set* objects found in the output file.
    
    Raises
    ----------
    OutputException
        If no Basis Set information is found in the file.
    
    ParsingException
        If an error occurs during the parsing of the data.
    
    GhostException
        If the parser finds an unexpected ghost atom in the Basis Set section of the output file.

        
    """
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.atoms: list[Atom] = []
        self.basis_sets: list[CrystalBasisSet] = []
        return self.__read_output()

    def __read_output(self) -> None:
        # control variables
        inside_ghost_section = False
        ghost_lines: list[str] = []
        inside_basis_set_section = False
        basis_set_lines: list[str] = []
        # Gather data
        with open(self.filepath, "r", encoding="utf-8") as output_file:
            for line in output_file:
                if "ATOMS TRANSFORMED INTO GHOSTS" in line:
                    inside_ghost_section = True
                if "LOCAL ATOMIC FUNCTIONS BASIS SET" in line:
                    inside_basis_set_section = True
                if inside_ghost_section:
                    if "****" in line:
                        inside_ghost_section = False
                    else:
                        ghost_lines.append(line.strip("\n"))
                if inside_basis_set_section:
                    if "INFORMATION" in line:
                        inside_basis_set_section = False
                        break
                    else:
                        basis_set_lines.append(line.strip("\n"))
        # Check data
        if len(basis_set_lines) == 0:
            raise OutputException("Couldn't find Basis Set information. Please double check the file.")
        
        # Parse information
        return self.__parse(ghost_lines, basis_set_lines)
    
    @staticmethod
    def __create_new_atom(regex_match: Iterable[str]) -> Atom:
        label, atomic_number, x, y, z = regex_match
        element = PeriodicTable.get_element(atomic_number)
        atom = Atom(int(label), element)
        atom.x, atom.y, atom.z = float(x), float(y), float(z)
        return atom
    
    @staticmethod
    def __create_new_function(regex_match: tuple[str]) -> BasisFunction:
        function_type = regex_match[-1]
        basis_function = BasisFunction(FunctionTypeSingleton.get(function_type))
        return basis_function

    @staticmethod
    def __create_new_primitive(regex_match: list[str]) -> PrimitiveFunction:
        exponent, s_coeff, p_coeff, dfg_coeff = regex_match
        return PrimitiveFunction(float(exponent), float(s_coeff), float(p_coeff), float(dfg_coeff))

    def __parse(self, ghost_lines: list[str], basis_set_lines: list[str]) -> None:
        GHOST_REGEX = r"(\d+)\(\s+(\d+)\)"
        ATOM_REGEX = r"\s+(\d+)\s+(\w+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)"
        FUNCTION_REGEX = r"^\s+(\d+)?-?\s+(\d+)\s(\w+)\s+$"
        PRIMITIVE_REGEX = r"\s?(-?\d\.\d+E[+-]\d\d)"

        # Recognize the ghost atoms as (label, element) tuples
        ghost_matches = []
        for line in ghost_lines:
            match = re.findall(GHOST_REGEX, line)
            if len(match) > 0:
                for tup in match:
                    label, atomic_number = tup
                    new_tup = (int(label), int(atomic_number))
                    ghost_matches.append(new_tup)
        
        # Read the basis set information
        current_atom: Atom | None = None
        current_basis_set: CrystalBasisSet | None = None
        current_function: BasisFunction | None = None

        for line in basis_set_lines:
            if atom_match := re.findall(ATOM_REGEX, line):
                # Finding a new atom means the end of the basis set section, if any
                if current_basis_set:
                    self.basis_sets.append(current_basis_set)
                    current_basis_set, current_function = None, None
                # Create the new atom
                current_atom = self.__create_new_atom(atom_match[0])
                self.atoms.append(current_atom)

            if function_match := re.findall(FUNCTION_REGEX, line):
                # If there is no current basis set, then create a new basis set
                if not current_basis_set:
                    current_basis_set = CrystalBasisSet()
                    if not current_atom:
                        raise ParsingException("Could not read current element of the new basis set.")
                    current_basis_set.element = current_atom.element
                # Create the new function
                current_function = self.__create_new_function(function_match[0])
                current_basis_set.basis_functions.append(current_function)
            
            if primitive_match := re.findall(PRIMITIVE_REGEX, line):
                primitive = self.__create_new_primitive(primitive_match)
                if not current_function:
                    raise ParsingException("Could not link primitive function to a basis function.")
                current_function.primitives.append(primitive)


if __name__ == "__main__":
    output = CrystalOutput("FTO_many_vac_test.out")
    print(f"{'LABEL':<5}{f'ELEMENT':>12}{'X':>12}{'Y':>10}{'Z':>10}")
    for atom in output.atoms:
        print(atom)
    for basis_set in output.basis_sets:
        print(basis_set)