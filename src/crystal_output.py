from dataclasses import dataclass

from atom import Atom
from basis_set import BasisSet


@dataclass
class CrystalOutput:
    atoms: list[Atom]
    basis_sets: list[BasisSet]
