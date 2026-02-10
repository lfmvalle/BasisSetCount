import re

# Argument parsing patterns
NUMBER_ARG_REGEX = re.compile(r"^[0-9]+$")
RANGE_ARG_REGEX = re.compile(r"^[0-9]+-[0-9]+$")

# File parsing patterns
GHOST_REGEX = re.compile(r"(\d+)\(\s+(\d+)\)")
ATOM_REGEX = re.compile(r"\s+(\d+)\s+(\w+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)")
FUNCTION_REGEX = re.compile(r"^\s+(\d+)?-?\s+(\d+)\s(\w+)\s+$")
PRIMITIVE_REGEX = re.compile(r"\s?(-?\d\.\d+E[+-]\d\d)")
