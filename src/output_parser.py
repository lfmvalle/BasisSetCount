from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional
import re

from atom import Atom
from basis_set import BasisSet, BasisFunction, PrimitiveFunction, FunctionType
from crystal_output import CrystalOutput
from exceptions import OutputException, ParsingException, GhostException, format_traceback
from logger import Logger
from periodic_table import PeriodicTable
from population_analysis import MullikenPopulation, AlphaBetaPair
import regex_pattern


class OutputRegion(Enum):
    InitialRegion = 0
    PseudoRegion = 1
    GhostRegion = 2
    BasisSetRegion = 3
    MullikenSum = 4
    MullikenSumValues = 5
    MullikenDiff = 6
    MullikenDiffValues = 7
    Unknown = 8


class LineType(Enum):
    PseudoLine = 0
    GhostAtomsLine = 1
    AtomLine = 2
    BasisFunctionLine = 3
    PrimitiveFunctionLine = 4
    MullikenAtom = 5
    MullikenOrbitals = 6
    Nothing = 7


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
        self.pseudo_basis_sets = []

        self.current_atom: Optional[Atom] = None
        self.current_basis_set: Optional[BasisSet] = None
        self.current_basis_function: Optional[BasisFunction] = None

        self.mulliken_buffer: list[str] = []
        self.mulliken_sums: list[list[str]] = []  # alpha + beta
        self.mulliken_diffs: list[list[str]] = []  # alpha - beta

    def feed(self, line: str) -> None:
        # Entering output region
        if "PSEUDOPOTENTIAL INFORMATION" in line and self.current_output_region == OutputRegion.InitialRegion:
            Logger.debug(f"Entering pseudopotential region: [bold]declaration of effective core potential basis sets[/]")
            self.current_output_region = OutputRegion.PseudoRegion
        elif "ATOMS TRANSFORMED INTO GHOSTS" in line:
            Logger.debug(f"Entering output region: [bold]declaration of ghost atoms[/]")
            self.current_output_region = OutputRegion.GhostRegion
        elif "LOCAL ATOMIC FUNCTIONS BASIS SET" in line:
            Logger.debug(f"Entering output region: [bold]definition of basis sets[/]")
            self.current_output_region = OutputRegion.BasisSetRegion
        elif "INFORMATION" in line and self.current_output_region == OutputRegion.BasisSetRegion:
            self.current_output_region = OutputRegion.Unknown
        elif "ALPHA+BETA ELECTRONS" in line:
            Logger.debug(f"Entering output region: [bold]α+β Mulliken Population[/]")
            self.current_output_region = OutputRegion.MullikenSum
        elif "ALPHA-BETA ELECTRONS" in line:
            Logger.debug(f"Entering output region: [bold]α-β Mulliken Population[/]")
            self.current_output_region = OutputRegion.MullikenDiff
        elif "ATOM" in line:
            match self.current_output_region:
                case OutputRegion.MullikenSum:
                    Logger.debug(f"Entering output region: [bold]α+β Mulliken Population[/] - [purple]A.O. population[/]")
                    self.current_output_region = OutputRegion.MullikenSumValues
                case OutputRegion.MullikenDiff:
                    Logger.debug(f"Entering output region: [bold]α-β Mulliken Population[/] - [purple]A.O. population[/]")
                    self.current_output_region = OutputRegion.MullikenDiffValues
        
        # Act according to output region
        match self.current_output_region:
            case OutputRegion.Unknown:
                return
            case OutputRegion.PseudoRegion:
                return self._parse_pseudo_line(line)
            case OutputRegion.GhostRegion:
                return self._parse_ghost_line(line)
            case OutputRegion.BasisSetRegion:
                return self._parse_basis_set_line(line)
            case OutputRegion.MullikenSumValues:
                return self._parse_mulliken_population(line)
            case OutputRegion.MullikenDiffValues:
                return self._parse_mulliken_population(line)
            case _:
                return

    def build(self) -> CrystalOutput:
        Logger.debug("Building output object...")
        if not self.atoms or not self.basis_sets:
             raise OutputException("Couldn't find information in the given output file. Please double check the file.")
        
        encountered_ghosts = 0
        expected_ghosts = len(self.ghost_atoms_tuples)
        for atom in self.atoms:
            # ensure all atoms point to a basis set
            if atom.basis_set is None:
                raise OutputException(f"No basis set attributed to [purple]Atom {atom.label}[/].")
            # count ghost atoms 
            if atom.is_ghost:
                encountered_ghosts += 1
        
        # verifify the number of ghost atoms
        if encountered_ghosts != expected_ghosts:
            raise OutputException(f"Expected [purple]{expected_ghosts}[/] ghost atoms: found only [purple]{encountered_ghosts}[/].")
        
        Logger.info(f"Number of atoms: [purple]{len(self.atoms)}[/]")
        Logger.info(f"Number of ghost atoms: [purple]{encountered_ghosts}[/]")
        Logger.info(f"Number of unique basis sets: [purple]{len(self.basis_sets)}[/]")

        # Mulliken
        if len(self.mulliken_diffs) == 0:
            Logger.info("Mulliken Population: [italic purple]restricted shell[/]")
            # Closed-Shell system: α-β buffer as zero-ed replicate of α+β buffer
            for buffer in self.mulliken_sums:
                new_buffer = []
                for i in buffer:
                    if "." in i:
                        new_buffer.append("0.000")
                    else:
                        new_buffer.append(i)
                self.mulliken_diffs.append(new_buffer)
        else:
            Logger.info("Mulliken Population: [italic purple]unrestricted shell[/]")
        
        self._build_mulliken_objects()
        return CrystalOutput(self.atoms, self.basis_sets)
    
    def _parse_pseudo_line(self, line: str) -> None:
        match = self._get_line_type(line)

        if match.line_type != LineType.Nothing:
            self.pseudo_basis_sets += match.content

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
                        raise GhostException(f"Unexpected ghost atom found: [purple]Atom {new_atom.label}[/]")

                # Exists a basis set for this atom?
                for basis_set in self.basis_sets:
                    # Yes, it exists
                    if basis_set.element == new_atom.element:
                        new_atom.basis_set = basis_set
                # No, create a new basis set
                if new_atom.basis_set is None:
                    is_pseudo_basis_set = False
                    for pseudo in self.pseudo_basis_sets:
                        element = PeriodicTable.get_element(int(pseudo))
                        if element == new_atom.element:
                            is_pseudo_basis_set = True
                            break
                    new_basis_set = BasisSet(new_atom.element, [], is_pseudo_basis_set)
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
        match self.current_output_region:
            case OutputRegion.BasisSetRegion:
                if atom_match := re.findall(regex_pattern.ATOM_REGEX, line):
                    return LineMatch(LineType.AtomLine, atom_match)
                elif function_match := re.findall(regex_pattern.FUNCTION_REGEX, line):
                    return LineMatch(LineType.BasisFunctionLine, function_match)
                elif primitive_match := re.findall(regex_pattern.PRIMITIVE_REGEX, line):
                    return LineMatch(LineType.PrimitiveFunctionLine, primitive_match)
            case OutputRegion.GhostRegion:
                if ghost_match := re.findall(regex_pattern.GHOST_REGEX, line):
                    return LineMatch(LineType.GhostAtomsLine, ghost_match)
            case OutputRegion.PseudoRegion:
                if pseudo_match := re.findall(regex_pattern.PSEUDO_REGEX, line):
                    return LineMatch(LineType.PseudoLine, pseudo_match)
            case OutputRegion.MullikenSumValues:
                if atom_match := re.findall(regex_pattern.MULLIKEN_ATOM_REGEX, line):
                    orbital_match = re.findall(regex_pattern.MULLIKEN_FLOAT3_REGEX, line)
                    return LineMatch(LineType.MullikenAtom, atom_match + orbital_match)
                elif orbital_match := re.findall(regex_pattern.MULLIKEN_FLOAT3_REGEX, line):
                    return LineMatch(LineType.MullikenOrbitals, orbital_match)
            case OutputRegion.MullikenDiffValues:
                if atom_match := re.findall(regex_pattern.MULLIKEN_ATOM_REGEX, line):
                    orbital_match = re.findall(regex_pattern.MULLIKEN_FLOAT3_REGEX, line)
                    return LineMatch(LineType.MullikenAtom, atom_match + orbital_match)
                elif orbital_match := re.findall(regex_pattern.MULLIKEN_FLOAT3_REGEX, line):
                    return LineMatch(LineType.MullikenOrbitals, orbital_match)
        return LineMatch(LineType.Nothing, [])

    @staticmethod
    def _new_atom(regex_match: list[str]) -> Atom:
        label, atomic_number, x, y, z = regex_match[0]
        element = PeriodicTable.get_element(atomic_number)
        return Atom(int(label), element, None, Decimal(x), Decimal(y), Decimal(z), False)
    
    @staticmethod
    def _new_basis_function(regex_match: list[str]) -> BasisFunction:
        function_type = regex_match[0][-1]
        return BasisFunction(FunctionType[function_type], [])
    
    @staticmethod
    def _new_primitive(regex_match: list[str]) -> PrimitiveFunction:
        exponent, s_coeff, p_coeff, dfg_coeff = regex_match
        return PrimitiveFunction(Decimal(exponent), Decimal(s_coeff), Decimal(p_coeff), Decimal(dfg_coeff))
    
    def _consume_mulliken_buffer(self) -> None:
        if not self.mulliken_buffer:
            return
        match self.current_output_region:
            case OutputRegion.MullikenSumValues:
                self.mulliken_sums.append(self.mulliken_buffer)
            case OutputRegion.MullikenDiffValues:
                self.mulliken_diffs.append(self.mulliken_buffer)
        
        self.mulliken_buffer = []
    
    def _can_build_mulliken_objects(self) -> bool:
        try:
            if len(self.mulliken_sums) != len(self.mulliken_diffs):
                Logger.debug(f"Length of [bold]α+β buffer[/] ([bold purple]{len(self.mulliken_sums)}[/]) differs from the length of [bold]α-β buffer[/] ([bold purple]{len(self.mulliken_diffs)}[/]).")
                return False
            if len(self.mulliken_sums) != len(self.atoms):
                Logger.debug(f"Length of [bold]α+β buffer[/] ([bold purple]{len(self.mulliken_sums)}[/]) differs from the total number of atoms ([bold purple]{len(self.atoms)}[/]).")
                return False
            
            for i, atom in enumerate(self.atoms):
                # Lengths are ok?
                sum_population = self.mulliken_sums[i]
                diff_population = self.mulliken_diffs[i]
                if len(sum_population) != len(diff_population):
                    Logger.debug(f"Length of [bold]α+β population[/] ([purple]{len(sum_population)}[/]) differs from the length of [bold]α-β population[/] ([purple]{len(diff_population)}[/]) for atom [bold]{atom.label}[/].")
                    return False
                # Labels are ok?
                if not int(sum_population[0]) == atom.label:
                    Logger.debug(f"Expected [bold]α+β population[/] for atom [purple]{atom.label}[/] but found atom [purple]{sum_population[0]}[/].")
                    return False
                if not int(diff_population[0]) == atom.label:
                    Logger.debug(f"Expected [bold]α-β population[/] for atom [purple]{atom.label}[/] but found atom [purple]{diff_population[0]}[/].")
                    return False
                # Elements are ok?
                sum_element = PeriodicTable.get_element(int(sum_population[1]))
                diff_element = PeriodicTable.get_element(int(diff_population[1]))
                if not sum_element == atom.element:
                    # is not ghost
                    if not sum_element.atomic_number == 0:
                        Logger.debug(f"Expected [purple]Z = {atom.element.atomic_number}[/] for [purple]Atom {atom.label}[/] but found [purple]Z = {sum_element.atomic_number}[/] in [bold]α+β population[/].")
                        return False
                if not diff_element == atom.element:
                    # is not ghost
                    if not sum_element.atomic_number == 0:
                        Logger.debug(f"Expected [purple]Z = {atom.element.atomic_number}[/] for [purple]Atom {atom.label}[/], but found [purple]Z = {diff_element.atomic_number}[/] in [bold]α-β population[/].")
                        return False
                # There is a basis set for the element?
                found_bs = [bs.element for bs in self.basis_sets]
                if not sum_element in found_bs:
                    # is not ghost
                    if not sum_element.atomic_number == 0:
                        Logger.debug(f"No basis set for [purple]Atom {atom.label}[/] with [purple]Z = {sum_element.atomic_number}[/].")
                        return False
            return True
        except Exception as exc:
            Logger.debug("Unexpected error while checking [italic]Mulliken Population Analysis[/].")
            Logger.debug(format_traceback(exc))
            return False

    def _build_mulliken_objects(self) -> None:
        Logger.debug(f"Building Mulliken objects")
        if not self._can_build_mulliken_objects():
            Logger.warn("Unable to handle [italic]Mulliken Population Analysis[/]")
            return

        for i, atom in enumerate(self.atoms):
            # change values from populations to decimal
            sum_charge, *sum_values = [Decimal(x) for x in self.mulliken_sums[i][2:]]
            diff_charge, *diff_values = [Decimal(x) for x in self.mulliken_diffs[i][2:]]
            mul_pop = MullikenPopulation(sum_charge, diff_charge, [])
            # create population objects
            for i in range(len(sum_values)):
                alpha = (sum_values[i] + diff_values[i]) / 2
                beta = sum_values[i] - alpha
                mul_pop.orbitals.append(AlphaBetaPair(alpha, beta))
            atom.mulliken = mul_pop

    def _parse_mulliken_population(self, line: str) -> None:
        line_match = self._get_line_type(line)

        # flag the end of Mulliken A+B and A-B regions
        match line_match.line_type:
            case LineType.Nothing:
                if not len(self.mulliken_buffer) > 0:
                    return
                self._consume_mulliken_buffer()
                self.current_output_region = OutputRegion.Unknown
                return
            case LineType.MullikenAtom:
                self._consume_mulliken_buffer()
                self.mulliken_buffer += line_match.content
            case LineType.MullikenOrbitals:
                self.mulliken_buffer += line_match.content