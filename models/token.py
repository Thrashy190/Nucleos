from dataclasses import dataclass

@dataclass
class Token:
    type: str     # Tipo de token (RESERVADA, ID, ENTERO, etc.)
    value: str    # Valor del lexema
    line: int     # Línea donde fue encontrado
    column: int   # Columna en la línea