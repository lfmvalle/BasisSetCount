from pathlib import Path
import yaml

from element import Element
from exceptions import ApplicationException
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

def init_resources():
    if not load_periodic_table():
        raise ApplicationException("Failed to load Periodic Table.")
