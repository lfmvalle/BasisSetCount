from enum import Enum
import re
import os
import sys

class BasisFunction:
    def __init__(self) -> None:
        self.exponent: float
        self.s_coeff: float
        self.p_coeff: float
        self.dfg_coeff: float

class AtomicOrbitalType(Enum):
    S = 'S'
    SP = 'SP'
    P = 'P'
    D = 'D'
    F = 'F'
    G = 'G'

class AtomicOrbital:
    def __init__(self) -> None:
        self.type: AtomicOrbitalType
        self.basis_functions: list[BasisFunction] = []

class BasisSet:
    def __init__(self) -> None:
        self.atom: str = ''
        self.atomic_orbitals: list[AtomicOrbital] = []

class Atom:
    def __init__(self) -> None:
        self.x = 0.
        self.y = 0.
        self.z = 0.
        self.label: int
        self.element: str
        self.basis_set: BasisSet
    
    def set_coordinates(self, coord: tuple[float, float, float]) -> None:
        self.x, self.y, self.z = coord[0], coord[1], coord[2]

class OutputParser:
    def __init__(self) -> None:
        self.atoms: list[Atom] = []
        self.basis_sets: list[BasisSet] = []
        self.gathering_basis_set = False
        self.atomRegex = r"\s+(\d+)\s+(\w+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)"
        self.orbitalRegex = r"^\s+(\d+)?-?\s+(\d+)\s(\w+)\s+$"
        self.functionRegex = r"\s?(-?\d\.\d+E[+-]\d\d)"
        self.current_basis_set: BasisSet | None = None

    def parse(self, filepath) -> None:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                # Local atomic functions basis set
                # Gathers: atom label, atom, atom position in a.u. (Bohr), and basis set type, exponent and coefficients
                if "LOCAL ATOMIC FUNCTIONS BASIS SET" in line:
                    self.gathering_basis_set = True
                # Is gathering basis set?
                if self.gathering_basis_set:
                    done = self.basis_set_parsing(line)
                    if done:
                        self.gathering_basis_set = False
                        # Link basis sets to atoms
                        for atom in self.atoms:
                            for basis_set in self.basis_sets:
                                if atom.element == basis_set.atom:
                                    atom.basis_set = basis_set
                                    break
                                # Vacancy: gets the last basis set (may be erroneous if vacancy is the first atom to present new basis set)
                                if "X" in atom.element:
                                    atom.basis_set = self.basis_sets[-1]
        if len(self.basis_sets) == 0 or len(self.atoms) == 0:    
            print(f"[ERROR] Could not find basis sets in \'{filepath}\'.")
            sys.exit()
    
    def basis_set_parsing(self, line) -> bool:
        # Try header
        if any(s in line for s in ["******", "D/F/G", "LOCAL ATOMIC FUNCTION"]):
            return False
        # Try new atom
        atom_data = re.findall(self.atomRegex, line)
        if atom_data:
            data = atom_data[0]  # gets the tuple from list of results
            new_atom = Atom()
            new_atom.label = int(data[0])
            new_atom.element = str(data[1]).capitalize()
            new_atom.x, new_atom.y, new_atom.z = float(data[2]), float(data[3]), float(data[4])
            self.atoms.append(new_atom)
            # Checks if there is any basis set finished and appends it to basis set list
            if self.current_basis_set is not None:
                self.basis_sets.append(self.current_basis_set)
                self.current_basis_set = None
            return False
        # Try new atomic orbital
        orbital_data = re.findall(self.orbitalRegex, line)
        if orbital_data:
            data = orbital_data[0] # gets the tuple from list of results
            # If no basis set is being filled, creates a new one
            if self.current_basis_set is None:
                self.current_basis_set = BasisSet()
                self.current_basis_set.atom = self.atoms[-1].element  # gets last atom added to represent the basis set
            # creates the new atomic orbital
            new_atomic_orbital = AtomicOrbital()
            new_atomic_orbital.type = data[-1]
            # appends new atomic orbital to basis set
            self.current_basis_set.atomic_orbitals.append(new_atomic_orbital)
            return False
        # Try new basis function
        basis_function_data = re.findall(self.functionRegex, line)
        if basis_function_data:
            data = basis_function_data
            new_basis_function = BasisFunction()
            new_basis_function.exponent = float(data[0])
            new_basis_function.s_coeff = float(data[1])
            new_basis_function.p_coeff = float(data[2])
            new_basis_function.dfg_coeff = float(data[3])
            return False
        # If none above, then it's finished gathering basis sets
        # but first checks if there is any basis set finished and appends it to basis set list
        if self.current_basis_set is not None:
            self.basis_sets.append(self.current_basis_set)
            self.current_basis_set = None
        return True

def validate() -> str:
    if len(sys.argv) < 2:
        print(f"[ERROR] You must specify the path to a CRYSTAL output.")
        sys.exit()
    filepath = os.path.abspath(sys.argv[1])
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit()
    if not os.path.isfile(filepath):
        print(f"[ERROR] Path \'{filepath}\' does not point to a file.")
        sys.exit()
    if not os.access(filepath, os.R_OK):
        print(f"[ERROR] You do not have reading permission for \'{filepath}\'.")
        sys.exit()
    return filepath

def atoms_to_print() -> list[int]:
    list_of_atoms = []
    if len(sys.argv) > 2:
        atoms = sys.argv[2:]
        for atom in atoms:
            try:
                list_of_atoms.append(int(atom))
            except ValueError:
                continue
    return list_of_atoms

def main(*args, **kwargs) -> None:
    bohr = 0.529177
    list_of_atoms = atoms_to_print()
    filepath = validate()
    output = OutputParser()
    output.parse(os.path.abspath(filepath))
    c = 1
    printable = True
    for atom in output.atoms:
        if list_of_atoms:
            if atom.label in list_of_atoms:
                printable = True
            else:
                printable = False
        if printable:
            print('~'*80)
            x_lab = "X"
            y_lab = "Y"
            z_lab = "Z"
            x_bohr_lab = x_lab + " (a.u.)"
            y_bohr_lab = y_lab + " (a.u.)"
            z_bohr_lab = z_lab + " (a.u.)"
            print(f"LABEL\tATOM\t{x_lab:>7s}{y_lab:>10s}{z_lab:>10s}{x_bohr_lab:>15s}{y_bohr_lab:>11s}{z_bohr_lab:>11s}")
            x = f"{atom.x*bohr:.3f}"
            y = f"{atom.y*bohr:.3f}"
            z = f"{atom.z*bohr:.3f}"
            x_bohr = f"{atom.x:.3f}"
            y_bohr = f"{atom.y:.3f}"
            z_bohr = f"{atom.z:.3f}"
            print(f"{atom.label}\t{atom.element}\t{x:>7s}{y:>10s}{z:>10s}{x_bohr:>15s}{y_bohr:>11s}{z_bohr:>11s}")
        s_count = 1
        sp_count = 2
        p_count = 2
        d_count = 3
        f_count = 4
        for atomic_orbital in atom.basis_set.atomic_orbitals:
            if printable:
                print()
            match atomic_orbital.type:
                case 'S':
                    if printable:
                        print(f"\t{c}\t{s_count}s")
                    c += 1  # Increase atomic orbital counter
                    s_count += 1  # Increase orbital type counter
                case 'SP':
                    index = ['s', 'x', 'y', 'z']
                    for i in range(0, 4):
                        if printable:
                            print(f"\t{c}\t{sp_count}sp {index[i]}")
                        c += 1
                    sp_count += 1
                case 'P':
                    index = ['x', 'y', 'z']
                    for i in range(0, 3):
                        if printable:
                            print(f"\t{c}\t{p_count}p {index[i]}")
                        c += 1
                    p_count += 1
                case 'D':
                    index = ['z²-x²-y²', 'xz', 'yz', 'x²-y²', 'xy']
                    for i in range(0, 5):
                        if printable:
                            print(f"\t{c}\t{d_count}d {index[i]}")
                        c += 1
                    d_count += 1
                case 'F':
                    index = ['(2z²-3x²-3y²)z', '(4z²-x²-y²)x', '(4z²-x²-y²)y', '(x²-y²)z', 'xyz', '(x²-3y²)x', '(3x²-y²)y']
                    for i in range(0, 7):
                        if printable:
                            print(f"\t{c}\t{f_count}f {index[i]}")
                        c += 1
                    f_count += 1
                case _:
                    raise Exception(f"Couldn't identify atomic orbital type \'{atomic_orbital.type}\' of atom {atom.label}.")
            
            


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
