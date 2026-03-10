from dataclasses import dataclass
from decimal import Decimal


@dataclass
class AlphaBetaPair:
    alpha: Decimal
    beta: Decimal

@dataclass
class MullikenPopulation:
    alpha_charge: Decimal
    beta_charge: Decimal
    orbitals: list[AlphaBetaPair]
