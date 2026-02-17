from arguments import *
from atom import Atom
from basis_set import FunctionType, AtomicFunctions
from crystal_output import CrystalOutput
from logger import Logger
from table import Table, Header, Row, Cell, CellAlignment, CellContentType
from text_style import TextStyle


class Printer:
    def __init__(self, output: CrystalOutput) -> None:
        self.output = output
    
    def _atoms_info(self) -> list[Table]:
        Logger.request("Atoms from basis set region of output file:")
        # create table and table header
        header_row = Row([
            Cell("Label"), Cell("Element"), Cell("X (a.u.)"), Cell("Y (a.u.)"), Cell("Z (a.u.)"), Cell("Atomic orbitals")
        ])
        header = Header([header_row])
        table = Table(header, [])

        # populate rows of table with atoms
        c = 0
        local_count = 0
        last_count = 0
        for atom in self.output.atoms:
            if atom.basis_set is not None:
                for basis_function in atom.basis_set.basis_functions:
                    local_count += basis_function.function_type.value
            
            element_str = f"{atom.element.symbol} (ghost)" if atom.is_ghost else atom.element.symbol
            atom_row = Row([
                Cell(atom.label, content_type=CellContentType.DIGIT),
                Cell(element_str),
                Cell(atom.x, CellContentType.DECIMAL, precision=3),
                Cell(atom.y, CellContentType.DECIMAL, precision=3),
                Cell(atom.z, CellContentType.DECIMAL, precision=3),
                Cell(f"{last_count + 1: d}-{local_count}")
            ])
            if atom.is_ghost:
                atom_row.add_style(TextStyle.PURPLE)
            table.rows.append(atom_row)
            last_count = local_count
        # format table
        table.add_row_style.header(TextStyle.BOLD, 0)
        table.set_column_alignment.table(CellAlignment.LEFT, 0)
        table.set_column_alignment.table(CellAlignment.CENTER, 1)
        table.set_column_alignment.table(CellAlignment.CENTER_SPACE_PADDING, 2)
        table.set_column_alignment.table(CellAlignment.CENTER_SPACE_PADDING, 3)
        table.set_column_alignment.table(CellAlignment.CENTER_SPACE_PADDING, 4)
        table.set_column_alignment.table(CellAlignment.RIGHT, 5)
        table.set_column_size.table(6, 0)
        table.set_column_size.table(12, 1)
        table.set_column_size.table(12, 2)
        table.set_column_size.table(12, 3)
        table.set_column_size.table(12, 4)
        table.set_column_size.table(16, 5)
        return [table]

    def _basis_sets_info(self) -> list[Table]:
        Logger.request("Basis sets in the output file:")
        tables: list[Table] = []
        for basis_set in self.output.basis_sets:
            atoms_using = 0
            basis_function_count = 0
            primitive_count = 0
            for atom in self.output.atoms:
                if atom.basis_set == basis_set:
                    atoms_using += 1

            # header - title
            title = f"{basis_set.element.symbol} (Z = {basis_set.element.atomic_number}) - "
            title += "Effective Core Potential basis set" if basis_set.pseudo else "All-electron basis set"
            title_row = Row([
                Cell(title, alignment=CellAlignment.CENTER, size=80),
            ])
            title_row.add_style(TextStyle.BOLD)
            title_row.add_style(TextStyle.PURPLE)

            # header - atoms using the basis set
            atoms_using_row = Row([
                Cell(f"Used by {atoms_using} atoms", alignment=CellAlignment.CENTER, size=80)
            ])
            atoms_using_row.add_style(TextStyle.BOLD)
            atoms_using_row.add_style(TextStyle.PURPLE)

            # header - separator
            separator = Row([
                Cell("~" * 80, size=80)
            ])

            # header - table columns
            table_header_row = Row([
                Cell("Atomic function", alignment=CellAlignment.CENTER, size=16),
                Cell("Exponent", alignment=CellAlignment.CENTER, size=16),
                Cell("s coeff.", alignment=CellAlignment.CENTER, size=16),
                Cell("p coeff.", alignment=CellAlignment.CENTER, size=16),
                Cell("d/f/g coeff.", alignment=CellAlignment.CENTER, size=16)
            ])
            table_header_row.add_style(TextStyle.BOLD)
            header = Header([title_row, atoms_using_row, separator, table_header_row])
            table = Table(header, [])

            for basis_function in basis_set.basis_functions:
                basis_function_count += 1
                new_basis_function = True
                for primitive in basis_function.primitives:
                    primitive_count += 1
                    primitive_row = Row([
                        Cell(basis_function.function_type.name) if new_basis_function else Cell(),
                        Cell(primitive.exponent, CellContentType.BASE10, precision=3),
                        Cell(primitive.s_coeff, CellContentType.BASE10, precision=3),
                        Cell(primitive.p_coeff, CellContentType.BASE10, precision=3),
                        Cell(primitive.dfg_coeff, CellContentType.BASE10, precision=3)
                    ])
                    table.rows.append(primitive_row)
                    new_basis_function = False
            
            # format table
            table.set_column_alignment.content(CellAlignment.CENTER, 0)
            table.set_column_alignment.content(CellAlignment.CENTER_SPACE_PADDING, 1)
            table.set_column_alignment.content(CellAlignment.CENTER_SPACE_PADDING, 2)
            table.set_column_alignment.content(CellAlignment.CENTER_SPACE_PADDING, 3)
            table.set_column_alignment.content(CellAlignment.CENTER_SPACE_PADDING, 4)
            table.set_column_size.content(16, 0)
            table.set_column_size.content(16, 1)
            table.set_column_size.content(16, 2)
            table.set_column_size.content(16, 3)
            table.set_column_size.content(16, 4)
            tables.append(table)
        return tables
    
    def _parse_ghost_atoms(self) -> list[Table]:
        Logger.request("Ghost atoms in the output file:")
        tables: list[Table] = []
        for atom in self.output.atoms:
            if atom.is_ghost:
                tables += self._parse_atom(atom.label)
        return tables
    
    @staticmethod
    def _new_atomic_function_row(index: int, function: str) -> Row:
        return Row([
            Cell(),
            Cell(index, content_type=CellContentType.DIGIT),
            Cell(function),
        ])
    
    def _count_atom(self, sum: int, atom: Atom) -> list[Table]:
        if atom.basis_set is None:
            return []
        
        FUNCTION_MAP = {
            FunctionType.S: AtomicFunctions.S.value,
            FunctionType.SP: AtomicFunctions.SP.value,
            FunctionType.P: AtomicFunctions.P.value,
            FunctionType.D: AtomicFunctions.D.value,
            FunctionType.F: AtomicFunctions.F.value,
            FunctionType.G: AtomicFunctions.G.value,
        }

        # header - title
        title_row = Row([
            Cell(f"Atom {atom.label} - {atom.element.symbol} (ghost)" if atom.is_ghost else f"Atom {atom.label} - {atom.element.symbol}", size=48, alignment=CellAlignment.CENTER)
        ])
        title_row.add_style(TextStyle.BOLD)
        title_row.add_style(TextStyle.PURPLE)

        # header - basis set type
        basis_set_type_row = Row([
            Cell("Effective Core Potential basis set" if atom.basis_set.pseudo else "All-electron basis set", size=48, alignment=CellAlignment.CENTER)
        ])
        basis_set_type_row.add_style(TextStyle.BOLD)
        basis_set_type_row.add_style(TextStyle.PURPLE)

        # header - separator
        separator = Row([
            Cell("-" * 48, size=48)
        ])

        # header - table columns
        table_header_row = Row([
            Cell("Atomic function", size=16, alignment=CellAlignment.CENTER),
            Cell("Index", size=16, alignment=CellAlignment.CENTER),
            Cell("Atomic orbital", size=16, alignment=CellAlignment.CENTER)
        ])
        table_header_row.add_style(TextStyle.BOLD)
        
        header = Header([title_row, basis_set_type_row, separator, table_header_row])
        table = Table(header, [])

        for basis_function in atom.basis_set.basis_functions:
            funcion_row = Row([
                Cell(basis_function.function_type.name),
                Cell(),
                Cell(),
            ])
            table.rows.append(funcion_row)
            for function in FUNCTION_MAP[basis_function.function_type]:
                sum += 1
                orbital_row = self._new_atomic_function_row(sum, function)
                table.rows.append(orbital_row)
        table.set_column_alignment.content(CellAlignment.CENTER, 0)
        table.set_column_alignment.content(CellAlignment.CENTER, 1)
        table.set_column_alignment.content(CellAlignment.LEFT, 2)
        table.set_column_size.content(16, 0)
        table.set_column_size.content(16, 1)
        table.set_column_size.content(16, 2)
        return [table]
    
    def _parse_atom(self, label: int) -> list[Table]:
        local_count = 0
        tables: list[Table] = []
        for atom in self.output.atoms:
            if atom.basis_set is not None:
                if atom.label == label:
                    this_count = local_count
                    for basis_function in atom.basis_set.basis_functions:
                        this_count += basis_function.function_type.value
                    tables += self._count_atom(local_count, atom)
                    break
                else:
                    for basis_function in atom.basis_set.basis_functions:
                        local_count += basis_function.function_type.value
        return tables

    def _parse_number_argument(self, arg: NumberArgument) -> list[Table]:
        Logger.debug(f"Parsing number argument: {TextStyle.PURPLE}{arg.value}{TextStyle.NONE}")
        Logger.request(f"Enumeration for {TextStyle.PURPLE}Atom {arg.value}{TextStyle.NONE}:")
        return self._parse_atom(int(arg.value))
    
    def _parse_range_argument(self, arg: RangeArgument) -> list[Table]:
        Logger.debug(f"Parsing range argument: {TextStyle.PURPLE}{arg.value}{TextStyle.NONE}")
        Logger.request(f"Enumeration for {TextStyle.PURPLE}Atoms {arg.value}{TextStyle.NONE}:")
        limits = arg.value.split("-")
        x, y = int(limits[0]), int(limits[1]) + 1
        tables: list[Table] = []
        if x > y:
            for i in range(x, y - 2, -1):
                tables += self._parse_atom(i)
        else:
            for i in range(x, y):
                tables += self._parse_atom(i)
        return tables

    def _parse_parameter_argument(self, arg: ParameterArgument) -> list[Table]:
        Logger.debug(f"Parsing parameter argument: {TextStyle.PURPLE}{arg.value}{TextStyle.NONE}")
        if arg.value == "-a":
            return self._atoms_info()
        elif arg.value == "-b":
            return self._basis_sets_info()
        elif arg.value == "x":
            return self._parse_ghost_atoms()
        return []

    def parse_argument(self, arg: Argument) -> list[Table]:
        PARSE_MAP = {
            NumberArgument: self._parse_number_argument,
            RangeArgument: self._parse_range_argument,
            ParameterArgument: self._parse_parameter_argument
        }

        return PARSE_MAP[type(arg)](arg)