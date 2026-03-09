from element import Element
from exceptions import PeriodicTableException


class PeriodicTable:
    elements: list[Element] = []
    
    @classmethod
    def get_element(cls, key: str | int) -> Element:
        if isinstance(key, str):  # Lookup by symbol
            key = key.capitalize()
            for element in cls.elements:
                if element.symbol == key:
                    return element
        elif isinstance(key, int):  # Lookup by atomic number
            # for Effective Core Potential basis sets
            if key > 200:
                key %= 200
            if key < 0 or key > 118:
                raise PeriodicTableException(f"Invalid atomic number: '{key}'.")
            for element in cls.elements:
                if element.atomic_number == key:
                    return element
        raise PeriodicTableException(f"Element '{key}' does not exist.")