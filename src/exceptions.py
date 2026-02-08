class OutputException(Exception):
    """
    The ***Output Exception*** class is used when the end of the output file is reached during the parsing and no Basis Set information is gathered.
    """

class ParsingException(Exception):
    """
    The ***Parsing Exception*** class is used when a regex match is expected in the parsing logic but it does not occur.
    """

class GhostException(Exception):
    """
    The ***Ghost Exception*** class is used when the parser finds a ghost atom in the Basis Set section that was not previously declared in the ghost atoms section.
    """