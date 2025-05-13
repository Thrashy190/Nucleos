from dataclasses import dataclass

@dataclass
class SyntaxError:
    message: str
    value: str
    line: int
    column: int
