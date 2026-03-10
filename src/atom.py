from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from basis_set import BasisSet
from periodic_table import Element
from population_analysis import MullikenPopulation


@dataclass
class Atom:
    label: int
    element: Element
    basis_set: Optional[BasisSet]
    x: Decimal
    y: Decimal
    z: Decimal
    is_ghost: bool
    mulliken: Optional[MullikenPopulation] = None
