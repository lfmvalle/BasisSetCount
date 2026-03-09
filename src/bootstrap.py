from pathlib import Path
import yaml

from element import Element
from exceptions import ApplicationException
from orbitals import AtomicOrbitals
from periodic_table import PeriodicTable


BASE_DIR = Path(__file__).parent

def load_yaml(filepath: Path) -> dict:
    with open(filepath, "r", encoding="utf-8") as file:
        dict = yaml.safe_load(file)
    return dict

def load_periodic_table() -> bool:
    elements = load_yaml(BASE_DIR / "periodic_table.yaml")
    for element in elements:
        e = Element(element["atomic_number"],
                    element["name"],
                    element["symbol"])
        PeriodicTable.elements.append(e)
    if len(PeriodicTable.elements) != 119:
        return False
    return True

def load_orbitals() -> bool:
    try:
        orbitals = load_yaml(BASE_DIR / "orbitals.yaml")
        AtomicOrbitals.S = [f"s [{orb}]" for orb in orbitals["s"]] 
        AtomicOrbitals.SP = [f"sp [{orb}]" for orb in orbitals["sp"]] 
        AtomicOrbitals.P = [f"p [{orb}]" for orb in orbitals["p"]] 
        AtomicOrbitals.D = [f"d [{orb}]" for orb in orbitals["d"]] 
        AtomicOrbitals.F = [f"f [{orb}]" for orb in orbitals["f"]] 
        AtomicOrbitals.G = [f"g [{orb}]" for orb in orbitals["g"]] 
    except:
        return False

    S_ok = len(AtomicOrbitals.S) == 1
    SP_ok = len(AtomicOrbitals.SP) == 4
    P_ok = len(AtomicOrbitals.P) == 3
    D_ok = len(AtomicOrbitals.D) == 5
    F_ok = len(AtomicOrbitals.F) == 7
    G_ok = len(AtomicOrbitals.G) == 9
    all_ok = S_ok and SP_ok and P_ok and D_ok and F_ok and G_ok

    if not all_ok:
        return False
    return True

def init_resources():
    if not load_periodic_table():
        raise ApplicationException("Failed to load Periodic Table.")
    if not load_orbitals():
        raise ApplicationException("Failed to load Atomic Orbitals.")