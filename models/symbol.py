from dataclasses import dataclass

@dataclass
class Symbol:
    name: str
    type: str
    scope: str
    value: str = None
