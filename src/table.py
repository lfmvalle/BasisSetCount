from enum import Enum
from typing import Optional

from exceptions import CellException, TableException
from text_style import TextStyle


class CellContentType(Enum):
    TEXT = "s"
    DIGIT = "d"
    DECIMAL = "f"
    BASE10 = "E"


class CellAlignment(Enum):
    LEFT = "<"
    RIGHT = ">"
    CENTER = "^"
    LEFT_SPACE_PADDING = "< "
    RIGHT_SPACE_PADDING = "> "
    CENTER_SPACE_PADDING = "^ "


type CellContent = str | int | float


class Cell:
    def __init__(self,
                 content: Optional[CellContent] = None,
                 content_type: CellContentType = CellContentType.TEXT,
                 alignment: CellAlignment = CellAlignment.LEFT,
                 size: int = 8,
                 style: TextStyle | str = TextStyle.NONE,
                 precision: Optional[int] = None) -> None:
        self.content = content
        self.content_type = content_type
        self.alignment = alignment
        self.size = size
        self.style = style
        self.precision = precision
    
    def _validate_cell(self) -> None:
        match self.content_type:
            case CellContentType.TEXT:
                if self.content and not isinstance(self.content, str):
                    raise CellException(f"Content of TEXT cell must be of type 'str'.")
                match self.alignment:
                    case CellAlignment.LEFT_SPACE_PADDING:
                        self.alignment = CellAlignment.LEFT
                    case CellAlignment.CENTER_SPACE_PADDING:
                        self.alignment = CellAlignment.CENTER
                    case CellAlignment.RIGHT_SPACE_PADDING:
                        self.alignment = CellAlignment.RIGHT
            case CellContentType.DIGIT:
                if self.content and not isinstance(self.content, int):
                    raise CellException(f"Content of DIGIT cell must be of type 'int'.")
            case CellContentType.DECIMAL:
                if self.content and not isinstance(self.content, float):
                    raise CellException(f"Content of DECIMAL cell must be of type 'float'.")
                if not self.precision:
                    raise CellException("DECIMAL cell must have a precision.")
            case CellContentType.BASE10:
                if self.content and not isinstance(self.content, float):
                    raise CellException(f"Content of BASE10 cell must be of type 'float'.")
                if not self.precision:
                    raise CellException("BASE10 cell must have a precision.")

    def render(self) -> str:
        # raise exceptions before rendering if the cell object is inconsistent
        self._validate_cell()
        
        # create format string
        if self.content_type == CellContentType.TEXT or self.content_type == CellContentType.DIGIT:
            format = f"{self.alignment.value}{self.size}{self.content_type.value}"
        else:
            format = f"{self.alignment.value}{self.size}.{self.precision}{self.content_type.value}"
        
        # early return for empty cell
        if not self.content:
            match self.content_type:
                case CellContentType.TEXT:
                    return f"{"":{format}}"
                case CellContentType.DIGIT:
                    return f"{0:{format}}"
                case _:
                    return f"{0.0:{format}}"
        
        # Format the cell content
        cell_content = f"{self.content:{format}}" if self.content else f"{"":{format}}"
        
        final_string = f"{self.style}{cell_content}{TextStyle.NONE}"
        
        return final_string
    
    def __str__(self) -> str:
        return self.render()


class Row:
    def __init__(self, cells: list[Cell] = []) -> None:
        self.cells = cells
    
    @property
    def width(self) -> int:
        size = 0
        for cell in self.cells:
            size += cell.size
        return size
    
    def add_style(self, style: TextStyle) -> None:
        for cell in self.cells:
            cell.style += style
    
    def render(self) -> str:
        contents = ""
        for cell in self.cells:
            contents += cell.render()
        return contents + '\n'
    
    def __str__(self) -> str:
        return self.render()


class Header:
    def __init__(self, rows: list[Row] = [], top_char = "-", bottom_char = "-") -> None:
        self.rows = rows
        self.top_char = top_char
        self.bottom_char = bottom_char

    @property
    def width(self) -> int:
        if not self.rows:
            raise CellException("No rows in the header")
        width = self.rows[0].width
        for row in self.rows:
            if row.width != width:
                raise CellException("Wrong width")
        return width
    
    def render(self) -> str:
        header = f"{self.top_char * self.width}\n"
        for row in self.rows:
            header += row.render()
        header += f"{self.bottom_char * self.width}\n"
        return header

    def __str__(self) -> str:
        return self.render()


class TableColumnAlignment:
    def __init__(self, table: Table) -> None:
        self._table = table
    
    def header(self, alignment: CellAlignment, column_index: int) -> None:
        try:
            for row in self._table.header.rows:
                row.cells[column_index].alignment = alignment
        except IndexError:
            return

    def content(self, alignment: CellAlignment, column_index: int) -> None:
        try:
            for row in self._table.rows:
                row.cells[column_index].alignment = alignment
        except IndexError:
            return
    
    def table(self, alignment: CellAlignment, column_index: int) -> None:
        self.header(alignment, column_index)
        self.content(alignment, column_index)


class TableColumnSize:
    def __init__(self, table: Table) -> None:
        self._table = table
    
    def header(self, size: int, column_index: int) -> None:
        try:
            for row in self._table.header.rows:
                row.cells[column_index].size = size
        except IndexError:
            return
    
    def content(self, size: int, column_index: int) -> None:
        try:
            for row in self._table.rows:
                row.cells[column_index].size = size
        except IndexError:
            return
    
    def table(self, size: int, column_index: int) -> None:
        self.header(size, column_index)
        self.content(size, column_index)


class TableColumnStyle:
    def __init__(self, table: Table) -> None:
        self._table = table
    
    def header(self, style: TextStyle, column_index: int) -> None:
        try:
            for row in self._table.header.rows:
                row.cells[column_index].style += style
        except IndexError:
            return
    
    def content(self, style: TextStyle, column_index: int) -> None:
        try:
            for row in self._table.rows:
                row.cells[column_index].style += style
        except IndexError:
            return
    
    def table(self, style: TextStyle, column_index: int) -> None:
        self.header(style, column_index)
        self.content(style, column_index)


class TableRowStyle:
    def __init__(self, table: Table) -> None:
        self._table = table
    
    def header(self, style: TextStyle, row_index: int) -> None:
        try:
            self._table.header.rows[row_index].add_style(style)
        except IndexError:
            return
    
    def content(self, style: TextStyle, row_index: int) -> None:
        try:
            self._table.rows[row_index].add_style(style)
        except IndexError:
            return
    
    def table(self, style: TextStyle, row_index: int) -> None:
        self.header(style, row_index)
        self.content(style, row_index)


class Table:
    def __init__(self, header: Header, rows: list[Row]) -> None:
        self.header = header
        self.rows = rows
        self.set_column_alignment = TableColumnAlignment(self)
        self.set_column_size = TableColumnSize(self)
        self.add_column_style = TableColumnStyle(self)
        self.add_row_style = TableRowStyle(self)
       
    def add_style_to_header_row(self, style: TextStyle, row: int) -> None:
        try:
            for cell in self.header.rows[row].cells:
                cell.style += style
        except IndexError:
            return
    
    def add_style_to_content_row(self, style: TextStyle, row: int) -> None:
        try:
            for cell in self.rows[row].cells:
                cell.style += style
        except IndexError:
            return
    
    def add_style_to_odd_content_rows(self, style: TextStyle) -> None:
        for i in range(len(self.rows)):
            if i % 2 != 0:
                self.add_style_to_content_row(style, i)
    
    def add_style_to_even_content_rows(self, style: TextStyle) -> None:
        for i in range(len(self.rows)):
            if i % 2 == 0:
                self.add_style_to_content_row(style, i)

    def render(self) -> str:
        table = self.header.render()
        for row in self.rows:
            if row.width != self.header.width:
                raise TableException(f"Row {self.rows.index(row)} has width {row.width} and header has width {self.header.width}.")
            table += row.render()
        table += self.header.top_char * self.header.width
        return table
    
    def __str__(self) -> str:
        return self.render()


if __name__ == "__main__":
    cell1 = Cell("a", size=16, style=TextStyle.BOLDITALIC)
    cell2 = Cell("b", alignment=CellAlignment.CENTER)
    cell3 = Cell("c", alignment=CellAlignment.RIGHT, size=16)
    cell4 = Cell(1.12345, CellContentType.DECIMAL, precision=1, size=16)
    cell5 = Cell(1.12345, CellContentType.DECIMAL, precision=3, alignment=CellAlignment.CENTER)
    cell6 = Cell(1.12345, CellContentType.DECIMAL, precision=5, alignment=CellAlignment.RIGHT, size=16)
    row1 = Row([cell1, cell2, cell3])
    row2 = Row([cell4, cell5, cell6])
    rows = [row1, row2]
    header = Header([row1])
    contents = [row2, row2, row2, row2, row2, row2]
    table = Table(header, contents)
    table.add_column_style.table(TextStyle.GREEN, 1)
    table.add_column_style.header(TextStyle.BLUE, 0)
    
    print(table)