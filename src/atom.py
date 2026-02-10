from dataclasses import dataclass
from typing import Optional

from periodic_table import Element
from basis_set import BasisSet


@dataclass
class Atom:
    label: int
    element: Element
    basis_set: Optional[BasisSet]
    x: float
    y: float
    z: float
    is_ghost: bool
