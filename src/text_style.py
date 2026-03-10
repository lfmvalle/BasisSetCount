import re

import regex_pattern


def fetch_styles(styles: str) -> str:
    """
    Fetch the ANSI styles in a style string, returning a string with the ANSI styles found.
    
    A *style string* is the string between a pair of [ ], describing style keywords separated by whitespaces, such as:
    `[bold italic blue]`
    """
    styles = styles.strip()
    if not styles:
        return ""
    
    split = styles.split(" ")
    if len(split) == 0:
        return ""
    
    STYLE_MAP = {
        "/": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "italic": "\033[3m",
        "gray": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "purple": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }

    style_string = ""
    for s in split:
        try:
            style_string += STYLE_MAP[s]
        except KeyError:  # not a style string, return the same input
            return styles
    return style_string

def parse_styles(string: str) -> str:
    """
    Parses a string containing styles and returns the string with proper ANSI color styling.

    Example:
    `"This is [bold]bold text[/]."` returns `"This is \\033[1mbold text\\033[0m."`
    """
    styles = re.findall(regex_pattern.STYLE_REGEX, string)
    if len(styles) == 0:
        return string
    
    m = string
    for style in styles:
        style_string = fetch_styles(style)
        if style_string == style.strip():  # if is the same string, it is not a style string
            continue
        m = m.replace(f"[{style}]", style_string, count=1)
    
    return m

def printf(string: str):
    """
    A wrapper for printing strings with styles.
    """
    print(parse_styles(string))
