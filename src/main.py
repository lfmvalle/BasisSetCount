import os
import sys

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

def main() -> None:
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
