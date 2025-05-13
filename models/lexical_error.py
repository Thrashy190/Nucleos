from dataclasses import dataclass

@dataclass
class LexicalError:
    message: str  # Descripción del error
    value: str    # Valor que causó el error
    line: int     # Línea donde ocurrió
    column: int   # Columna en la línea
