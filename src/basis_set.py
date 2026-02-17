from dataclasses import dataclass
from enum import Enum

from periodic_table import Element


class FunctionType(Enum):
    S = 1
    SP = 4
    P = 3
    D = 5
    F = 7
    G = 9


class AtomicFunctions(Enum):
    S = ["s"]
    SP = ["s", "p [x]", "p [y]", "p [z]"]
    P = ["p [x]", "p [y]", "p [z]"]
    D = [
        "d [z2]",
        "d [xz]",
        "d [yz]",
        "d [x2y2]",
        "d [xy]"
        ]
    F = [
        "f [z2z]",
        "f [z2x]",
        "f [z2y]",
        "f [x2z]",
        "f [xyz]",
        "f [x2x]",
        "f [x2y]"
    ]
    G = [
        "g [x4z2]",
        "g [z2xz]",
        "g [z2yz]",
        "g [x2z2]",
        "g [z2xy]",
        "g [x2xz]",
        "g [x2yz]",
        "g [x4y4]",
        "g [x2xy]"
    ]


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
