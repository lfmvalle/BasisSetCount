from enum import Enum


class TextStyle(Enum):
    NONE = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    BOLDITALIC = "\033[1;3m"
    DARK = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"

    def __add__(self, other: object) -> str:
        if isinstance(other, TextStyle):
            return f"{self.value}{other.value}"
        if isinstance(other, str):
            return f"{self.value}{other}"
        raise TypeError("Adding TextStyle: object must be of type 'TextStyle' or 'str'.")
    
    def __radd__(self, other: object) -> str:
        if isinstance(other, TextStyle):
            return f"{other.value}{self.value}"
        if isinstance(other, str):
            return f"{other}{self.value}"
        raise TypeError("Adding TextStyle: object must be of type 'TextStyle' or 'str'.")
    
    def __str__(self) -> str:
        return self.value