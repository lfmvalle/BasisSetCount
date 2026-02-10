from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re

from atom import Atom
from basis_set import BasisSet, BasisFunction, PrimitiveFunction, FunctionType
from crystal_output import CrystalOutput
from exceptions import OutputException, ParsingException, GhostException
from logger import Logger
from periodic_table import PeriodicTable
import regex_pattern
import text_style


class OutputRegion(Enum):
    InitialRegion = 0
    GhostRegion = 1
    BasisSetRegion = 2
    StopRegion = 3


class LineType(Enum):
    GhostAtomsLine = 0
    AtomLine = 1
    BasisFunctionLine = 2
    PrimitiveFunctionLine = 3
    Nothing = 4


@dataclass
class LineMatch:
    line_type: LineType
    content: list[str]


class OutputParser:
    def __init__(self) -> None:
        # data used to build the output object
        self.atoms: list[Atom] = []
        self.basis_sets: list[BasisSet] = []

        self.current_output_region = OutputRegion.InitialRegion

        self.ghost_atoms_tuples = []

        self.current_atom: Optional[Atom] = None
        self.current_basis_set: Optional[BasisSet] = None
        self.current_basis_function: Optional[BasisFunction] = None

    def feed(self, line: str) -> None:
        # Change output region
        if "ATOMS TRANSFORMED INTO GHOSTS" in line and self.current_output_region:
            Logger.debug(f"Entering output region: {text_style.PURPLE}declaration of ghost atoms{text_style.NONE}.")
            self.current_output_region = OutputRegion.GhostRegion
        elif "LOCAL ATOMIC FUNCTIONS BASIS SET" in line:
            Logger.debug(f"Entering output region: {text_style.PURPLE}definition of basis sets{text_style.NONE}.")
            self.current_output_region = OutputRegion.BasisSetRegion
        elif "INFORMATION" in line and self.current_output_region == OutputRegion.BasisSetRegion:
            self.current_output_region = OutputRegion.StopRegion
        
        # Act according to output region
        match self.current_output_region:
            case OutputRegion.StopRegion:
                Logger.debug(f"Stopping output parsing: {text_style.PURPLE}end of the basis set region{text_style.NONE}.")
                raise StopIteration
            case OutputRegion.GhostRegion:
                return self._parse_ghost_line(line)
            case OutputRegion.BasisSetRegion:
                return self._parse_basis_set_line(line)

    def build(self) -> CrystalOutput:
        Logger.debug("Validating the output parsing...")
        if not self.atoms or not self.basis_sets:
             raise OutputException("Couldn't find information in the given output file. Please double check the file.")
        
        encountered_ghosts = 0
        expected_ghosts = len(self.ghost_atoms_tuples)
        for atom in self.atoms:
            # ensure all atoms point to a basis set
            if atom.basis_set is None:
                raise OutputException(f"No basis set attributed to {text_style.PURPLE}Atom {atom.label}{text_style.NONE}.")
            # count ghost atoms 
            if atom.is_ghost:
                encountered_ghosts += 1
        
        # verifify the number of ghost atoms
        if encountered_ghosts != expected_ghosts:
            raise OutputException(f"Expected {text_style.PURPLE}{expected_ghosts}{text_style.NONE} ghost atoms: found only {text_style.PURPLE}{encountered_ghosts}{text_style.NONE}.")
        
        Logger.info(f"Number of atoms: {text_style.PURPLE}{len(self.atoms)}{text_style.NONE}")
        Logger.info(f"Number of ghost atoms: {text_style.PURPLE}{encountered_ghosts}{text_style.NONE}")
        Logger.info(f"Number of unique basis sets: {text_style.PURPLE}{len(self.basis_sets)}{text_style.NONE}")

        Logger.debug("Building output object...")
        return CrystalOutput(self.atoms, self.basis_sets)
    
    def _parse_ghost_line(self, line: str) -> None:
        match = self._get_line_type(line)

        if match.line_type != LineType.Nothing:
            self.ghost_atoms_tuples += match.content

    def _parse_basis_set_line(self, line: str) -> None:
        line_match = self._get_line_type(line)

        match line_match.line_type:
            case LineType.AtomLine:
                new_atom = self._new_atom(line_match.content)
                
                # Is ghost atom?
                if new_atom.element.atomic_number == 0:
                    new_atom.is_ghost = True
                    for (label, atomic_number) in self.ghost_atoms_tuples:
                        if new_atom.label == int(label):
                            new_atom.element = PeriodicTable.get_element(int(atomic_number))
                            break
                    if new_atom.element.atomic_number == 0:
                        raise GhostException(f"Unexpected ghost atom found: {text_style.PURPLE}Atom {new_atom.label}{text_style.NONE}")

                # Exists a basis set for this atom?
                for basis_set in self.basis_sets:
                    # Yes, it exists
                    if basis_set.element == new_atom.element:
                        new_atom.basis_set = basis_set
                # No, create a new basis set
                if new_atom.basis_set is None:
                    new_basis_set = BasisSet(new_atom.element, [])
                    self.basis_sets.append(new_basis_set)
                    new_atom.basis_set = new_basis_set
                self.atoms.append(new_atom)

            case LineType.BasisFunctionLine:
                if len(self.basis_sets) == 0:
                    raise ParsingException("Found a basis function, but there's no basis set for it.")
                
                new_basis_function = self._new_basis_function(line_match.content)
                self.basis_sets[-1].basis_functions.append(new_basis_function)

            case LineType.PrimitiveFunctionLine:
                if len(self.basis_sets) == 0:
                    raise ParsingException("Found a primitive function, but there's no basis set for it.")
                if len(self.basis_sets[-1].basis_functions) == 0:
                    raise ParsingException("Found a primitive function, but there's no basis function for it.")

                new_primitive = self._new_primitive(line_match.content)
                self.basis_sets[-1].basis_functions[-1].primitives.append(new_primitive)

    def _get_line_type(self, line: str) -> LineMatch:
        if self.current_output_region == OutputRegion.BasisSetRegion:
            if atom_match := re.findall(regex_pattern.ATOM_REGEX, line):
                return LineMatch(LineType.AtomLine, atom_match)
            elif function_match := re.findall(regex_pattern.FUNCTION_REGEX, line):
                return LineMatch(LineType.BasisFunctionLine, function_match)
            elif primitive_match := re.findall(regex_pattern.PRIMITIVE_REGEX, line):
                return LineMatch(LineType.PrimitiveFunctionLine, primitive_match)
        if self.current_output_region == OutputRegion.GhostRegion:
            if ghost_match := re.findall(regex_pattern.GHOST_REGEX, line):
                return LineMatch(LineType.GhostAtomsLine, ghost_match)
        return LineMatch(LineType.Nothing, [])

    @staticmethod
    def _new_atom(regex_match: list[str]) -> Atom:
        label, atomic_number, x, y, z = regex_match[0]
        element = PeriodicTable.get_element(atomic_number)
        return Atom(int(label), element, None, float(x), float(y), float(z), False)
    
    @staticmethod
    def _new_basis_function(regex_match: list[str]) -> BasisFunction:
        function_type = regex_match[0][-1]
        return BasisFunction(FunctionType[function_type], [])
    
    @staticmethod
    def _new_primitive(regex_match: list[str]) -> PrimitiveFunction:
        exponent, s_coeff, p_coeff, dfg_coeff = regex_match
        return PrimitiveFunction(float(exponent), float(s_coeff), float(p_coeff), float(dfg_coeff))