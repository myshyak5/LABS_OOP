import json
from enum import Enum
from typing import Tuple, Dict, List

class Color(Enum):
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"
class Printer:
    def __init__(self, color: Color, position: Tuple[int, int], symbol: str, font_file: str):
        self.color = color
        self.position = position
        self.symbol = symbol
        self.font = self.load_font(font_file)
        self.original_position = None
    def load_font(self, font_file: str) -> Dict[str, List[str]]:
        with open(font_file, "r", encoding="utf-8") as f:
            return json.load(f)
    def move_cursor(self, position: Tuple[int, int]):
        row, col = position
        print(f"\033[{row};{col}H", end="")
    def print_char(self, char: str, base_row: int, base_col: int):
        char = char.upper()
        if char not in self.font:
            return
        lines = self.font[char]
        for i, line in enumerate(lines):
            self.move_cursor((base_row + i, base_col))
            pseudo_line = line.replace('*', self.symbol)
            print(f"{self.color.value}{pseudo_line}{Color.RESET.value}", end="")
    def print(self, text: str):
        base_row, base_col = self.position
        for char in text:
            self.print_char(char, base_row, base_col)
            base_col += self.get_char_width(char) + 1
    def get_char_width(self, char: str) -> int:
        char = char.upper()
        if char in self.font and self.font[char]:
            return len(self.font[char][0])
        return 1
    def __enter__(self):
        self.original_position = (0, 1)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(Color.RESET.value, end="")
        self.move_cursor(self.original_position)
    @classmethod
    def static_print(cls, text: str, color: Color, position: Tuple[int, int], symbol: str, font_file: str):
        printer = cls(color, position, symbol, font_file)
        printer.print(text)

if __name__ == "__main__":
    CLEAR = "\033[2J\033[H"
    print(CLEAR, end='')
    Printer.static_print(text="ABIC", color=Color.RED, position=(2, 1), symbol="*", font_file="font5.json")
    with Printer(color=Color.GREEN, position=(7, 1), symbol="#", font_file="font5.json") as printer:
        printer.print("ABIC")
    with Printer(color=Color.BLUE, position=(12, 1), symbol="@", font_file="font5.json") as printer:
        printer.print("ABCDE")