from dataclasses import dataclass
from enum import IntEnum

from periodic_table import Element


class FunctionType(IntEnum):
    S = 1
    SP = 4
    P = 3
    D = 5
    F = 7
    G = 9

@dataclass
class PrimitiveFunction:
    exponent: float
    s_coeff: float
    p_coeff: float
    dfg_coeff: float

@dataclass
class BasisFunction:
    function_type: FunctionType
    primitives: list[PrimitiveFunction]

@dataclass
class BasisSet:
    element: Element
    basis_functions: list[BasisFunction]
    pseudo: bool = False
