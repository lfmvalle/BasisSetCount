from dataclasses import dataclass


@dataclass
class Element:
    atomic_number: int
    name: str
    symbol: str
