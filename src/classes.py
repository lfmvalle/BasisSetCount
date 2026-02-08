from dataclasses import dataclass
import json

class PrimitiveFunction:
    """
    The ***Primitive Function*** class stores the numerical data of a single primitive function.
    
    In CRYSTAL, ***Primitive Functions*** are *Gaussian Type Functions* (GTFs).

    Parameters
    ----------
    exponent : float
        The alpha exponent of the ***Primitive Function***. Default is zero.

    s_coeff : float
        The contraction coefficient to be used for *s* type functions. Default is zero.

    p_coeff: float
        The contraction coefficient to be used for *p* type functions. Default is zero.

    dfg_coeff : float
        The contraction coefficient to be used for *d*, *f*, and/or *g* type functions. Default is zero.
    """
    def __init__(self,
                 exponent: float = .0,
                 s_coeff: float = .0,
                 p_coeff: float = .0,
                 dfg_coeff: float = .0) -> None:
        self.exponent = exponent
        self.s_coeff = s_coeff
        self.p_coeff = p_coeff
        self.dfg_coeff = dfg_coeff
    
    def __str__(self) -> str:
        string = f"{self.exponent:< 15f}{self.s_coeff:< 15f}{self.p_coeff:< 15f}{self.dfg_coeff:< 15f}"
        return string

@dataclass
class FunctionType:
    """
    The ***Function Type*** dataclass holds information about a given *Basis Function* type.

    Parameters
    ----------
    function_type: str
        Allowed types: *S*, *SP*, *P*, *D*, *F*, or *G*.
    """
    function_type: str  # the name of the function type
    ml: list[str]  # magnetic functions

class FunctionTypeSingleton:
    """
    Singleton class to handle the available types of *Basis Functions* in CRYSTAL.

    Allowed types:
        S - For *s* type functions (1 magnetic function)
        SP - For *sp* type functions (4 magnetic functions)
        P - For *p* type functions (3 magnetic functions)
        D - For *d* type functions (5 magnetic functions)
        F - For *f* type functions (7 magnetic functions)
        G - For *g* type functions (9 magnetic functions)
    """
    __function_types: list[FunctionType] = []

    @classmethod
    def get(cls, function_type: str) -> FunctionType:
        allowed_types = ["S", "SP", "P", "D", "F", "G"]
        if function_type not in allowed_types:
            raise ValueError(f"Basis Function type '{function_type}' is not allowed.")
        for t in cls.__function_types:
            if t.function_type == function_type:
                return t
        return cls.__create(function_type)

    @classmethod
    def __create(cls, function_type: str) -> FunctionType:
        ml_functions = {
            "S": ["s"],
            "SP": ["s", "x", "y", "z"],
            "P": ["x", "y", "z"],
            "D": [
                "z²-x-²y²",
                "xz",
                "yz",
                "x²-y²",
                "xy"],
            "F": [
                "(2z²-3x²-3y²)z",
                "(4z²-x²-y²)x",
                "(4z²-x²-y²)y",
                "(x²-y²)z",
                "xyz",
                "(x²-3y²)x",
                "(3x²-y²)y"],
            "G": [
                "3x⁴ + 6x²y² - 24x²z² + 3y⁴ - 24y²z² + 8z²",
                "(4z² - 3x² - 3y²)xz",
                "(4z² - 3x² - 3y²)yz",
                "6x²z² - x⁴ + y⁴ - 6y²z²",
                "(6z² - x² - y²)xy",
                "(x² - 3y²)xz",
                "(3x² - y²)yz",
                "x⁴ - 6x²y² + y⁴",
                "(x² - y²)xy"]
        }
        new_function = FunctionType(function_type, ml_functions[function_type])
        cls.__function_types.append(new_function)
        return new_function

class BasisFunction:
    """
    The ***Basis Function*** class describe a given *function* using a set of *Primitive Functions*.

    In CRYSTAL, ***Basis Functions*** are *Contracted Gaussian Type Functions* (CGTFs).

    Parameters
    ----------
    function_type : FunctionTypeEnum
        The type of function represented by the ***Basis Function***.

    Attributes
    ----------
    primitives : list[PrimitiveFunction]
        The list of *Primitive Functions* objects that describes the ***Basis Function***.
    """
    def __init__(self,
                 function_type: FunctionType) -> None:
        self.function_type = function_type
        self.primitives: list[PrimitiveFunction] = []
    
    def __str__(self) -> str:
        string = f"{self.function_type.function_type}\n"
        for primitive in self.primitives:
            string += f"\t\t{primitive}\n"
        return string


class CrystalBasisSet:
    """
    The ***Basis Set*** class describe Atomic Orbitals by a set of *Basis Functions*.

    In CRYSTAL, the Atomic Orbitals in a ***Basis Set*** are *Gaussian Type Orbitals* (GTOs).
    
    Attributes
    ----------
    basis_functions : list[BasisFunction]
        The list of *Basis Functions* objects that describes the ***Basis Set***.
    """
    def __init__(self) -> None:
        self.element: Element
        self.basis_functions: list[BasisFunction] = []
    
    def __str__(self) -> str:
        string = f"Basis set for {self.element.symbol} ({self.element.atomic_number}):\n"
        string += f"\tTYPE\t{'EXPONENT':<16s}{'S COEFF':<15s}{'P COEFF':<15s}{'D/F/G COEFF':<15s}\n"
        for basis_function in self.basis_functions:
            string += f"\t{basis_function}\n"
        return string


class Element:
    """
    The ***Element*** class describes an element through its *symbol* and *atomic number* (Z).

    NOTE: Vacancies created using the ```GHOST``` keyword are represented by the symbol **Xx** and atomic number **0**.

    Parameters
    ----------
    symbol : str
        The symbol of the element. Use **Xx** for vacancies.
    
    atomic_number : int
        The atomic number (Z) of the element. Use **0** for vacancies.
    """
    def __init__(self,
                 symbol: str,
                 atomic_number: int) -> None:
        self.symbol = symbol.capitalize()
        self.atomic_number = atomic_number
    
    def __str__(self) -> str:
        return f"{self.symbol} ({self.atomic_number})"

    def __repr__(self) -> str:
        return f"Element({self.symbol}, {self.atomic_number})"

class Atom:
    """
    The ***Atom*** class associates a given *Element* to a *label*, a *Basis Set*, and a *xyz* coordinate.

    As CRYSTAL utilizes atom-centered basis sets, the *xyz* coordinate of the ***Atom*** also represents the center of the *Basis Set*.

    Parameters
    ----------
    label: int
        The label represents a unique ***Atom*** as an integer greater than zero.

    element: Element
        The element object for the ***Atom***.

    Attributes
    ----------
    basis_set : BasisSet
        The Basis Set for the ***Atom***.

    x: float
        The x coordinate for the ***Atom***/center of the basis set. Default is zero.
    
    y: float
        The y coordinate for the ***Atom***/center of the basis set. Default is zero.
    
    z: float
        The z coordinate for the ***Atom***/center of the basis set. Default is zero.
    """
    def __init__(self, label: int, element: Element) -> None:
        self.label = label
        self.element = element
        self.basis_set: CrystalBasisSet
        self.x: float = 0.
        self.y: float = 0.
        self.z: float = 0.
    
    def __str__(self) -> str:
        return f"{self.label:<10}{f'{self.element}':<15}{self.x:< 10}{self.y:< 10}{self.z:< 10}"

    def __repr__(self) -> str:
        return f"Atom({self.label}, {self.element})"


class PeriodicTable:
    """
    The ***Periodic Table*** class contains all the *Element* objects.
    """
    elements: list[Element] = []
    with open("elements.json", "r", encoding="utf-8") as elements_json:
        for element_dict in json.load(elements_json):
            element = Element(element_dict["symbol"], element_dict["atomic_number"])
            elements.append(element)

    @classmethod
    def get_element(cls, key: str | int) -> Element:
        """
        Returns the *Element* object that corresponds to the given key.

        Parameters
        ----------
        key : str | int
            The element symbol (str) or atomic number (int).
        
        Returns
        ----------
        The ***Element*** object corresponding to the symbol or atomic number.
        
        Raises
        ----------
        KeyError
            If the element is not found.
        
        ValueError
            If the atomic number is less than zero or greater than 118.
        """
        if isinstance(key, str):  # Lookup by symbol
            key = key.capitalize()
            for element in cls.elements:
                if element.symbol == key:
                    return element
        elif isinstance(key, int):  # Lookup by atomic number
            if key < 0 or key > 118:
                raise ValueError(f"Invalid atomic number: '{key}'.")
            for element in cls.elements:
                if element.atomic_number == key:
                    return element
        raise KeyError(f"Element with key '{key}' not found.")