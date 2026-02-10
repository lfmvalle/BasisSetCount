from dataclasses import dataclass
from pathlib import Path
import json

from exceptions import PeriodicTableException


@dataclass
class Element:
    symbol: str
    atomic_number: int


class PeriodicTable:
    elements: list[Element] = []
    _json_path = Path(__file__).resolve().parent / "periodic_table.json"
    
    with open(_json_path, "r", encoding="utf-8") as periodic_table:
        for element_dict in json.load(periodic_table):
            element = Element(element_dict["symbol"], int(element_dict["atomic_number"]))
            elements.append(element)

    @classmethod
    def get_element(cls, key: str | int) -> Element:
        if isinstance(key, str):  # Lookup by symbol
            key = key.capitalize()
            for element in cls.elements:
                if element.symbol == key:
                    return element
        elif isinstance(key, int):  # Lookup by atomic number
            # for Core-Effective Potential basis sets
            if key > 200:
                key %= 200
            if key < 0 or key > 118:
                raise PeriodicTableException(f"Invalid atomic number: '{key}'.")
            for element in cls.elements:
                if element.atomic_number == key:
                    return element
        raise PeriodicTableException(f"Element '{key}' does not exist.")