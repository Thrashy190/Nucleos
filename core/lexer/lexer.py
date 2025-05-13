import re
from models.token import Token
from models.lexical_error import LexicalError
import csv
from pathlib import Path

class Lexer:
    def __init__(self):
        self.tokens = []
        self.errors = []
        self.line_number = 1

        self.reserved_words = {
            "programa", "real", "leer", "haz", "default", "funcion", "cadena", "escribir", "mientras","entonces","hacer","repetir",
            "regresar", "vacio", "variables", "si", "encaso", "ejecutar", "entero", "sino", "caso", "logico","inicio", "fin","hasta"
        }

        self.operators = {
            "+": "SUMA", "-": "RESTA", "*": "MULTIPLICACION", "/": "DIVISION", "%": "MODULO", "=": "ASIGNACION",
            "<": "MENOR", "<=": "MENOR_IGUAL", ">": "MAYOR", ">=": "MAYOR_IGUAL", "==": "IGUAL", "!=": "DIFERENTE",
            "!": "NOT", "&&": "AND", "||": "OR"
        }

        self.symbols = {
            ";": "PUNTO_COMA", ",": "COMA", ":": "DOS_PUNTOS",
            "(": "PARENTESIS_ABRE", ")": "PARENTESIS_CIERRA",
            "{": "LLAVE_ABRE", "}": "LLAVE_CIERRA"
        }

        # Expresiones regulares para tokens válidos
        self.token_patterns = [
            (r'//.*', None),  # comentario en línea
            (r'/\*[\s\S]*?\*/', None),  # comentario multilinea
            (r'"[^"\n]*"', "CADENA"),
            (r'\d+\.\d+', "REAL"),
            (r'\d+', "ENTERO"),
            (r'\btrue\b|\bfalse\b', "BOOLEANO"),
            (r'[a-zA-Z][a-zA-Z0-9]*@', "ID_METODO"),
            (r'[a-zA-Z][a-zA-Z0-9]*&', "ID_ENTERO"),
            (r'[a-zA-Z][a-zA-Z0-9]*%', "ID_REAL"),
            (r'[a-zA-Z][a-zA-Z0-9]*\$', "ID_CADENA"),
            (r'[a-zA-Z][a-zA-Z0-9]*#', "ID_LOGICO"),
            (r'[a-zA-Z][a-zA-Z0-9]*', "ID"),
            (r'[a-zA-Z][a-zA-Z0-9]*[^\w@&%$\#]', "INVALIDO")  # ID mal formado
        ]

        self.multi_char_ops = ["==", "!=", "<=", ">=", "&&", "||"]

    def analyze(self, text):
        self.tokens.clear()
        self.errors.clear()

        lines = text.splitlines()

        for line_number, line in enumerate(lines, start=1):
            position = 0
            while position < len(line):
                current = line[position]

                if current in [' ', '\t', '\r', '\n']:
                    position += 1
                    continue

                # Comentarios
                if line[position:position+2] == "//":
                    break
                if line[position:position+2] == "/*":
                    end = line.find("*/", position)
                    if end == -1:
                        self.errors.append(LexicalError("Comentario multilinea no cerrado", "/*", line_number, position))
                        break
                    position = end + 2
                    continue

                # Operadores multicaracter
                matched = False
                for op in self.multi_char_ops:
                    if line[position:position+len(op)] == op:
                        self.tokens.append(Token("OPERADOR", op, line_number, position+1))
                        position += len(op)
                        matched = True
                        break
                if matched:
                    continue

                # Operadores y símbolos de un solo carácter
                if current in self.operators:
                    self.tokens.append(Token("OPERADOR", current, line_number, position+1))
                    position += 1
                    continue
                if current in self.symbols:
                    self.tokens.append(Token("SIMBOLO", current, line_number, position+1))
                    position += 1
                    continue

                # Literales, identificadores y errores léxicos
                for pattern, token_type in self.token_patterns:
                    regex = re.compile(pattern)
                    match = regex.match(line[position:])
                    if match:
                        lexeme = match.group(0)

                        if token_type is None:
                            position += len(lexeme)
                            break
                        elif token_type == "INVALIDO":
                            self.errors.append(LexicalError("Token inválido", lexeme, line_number, position+1))
                        elif token_type == "ID" and lexeme in self.reserved_words:
                            self.tokens.append(Token("RESERVADA", lexeme, line_number, position+1))
                        else:
                            self.tokens.append(Token(token_type, lexeme, line_number, position+1))

                        position += len(lexeme)
                        break
                else:
                    self.errors.append(LexicalError("Caracter no reconocido", current, line_number, position+1))
                    position += 1

    def export_to_csv(self):
        output_path = Path("output")
        output_path.mkdir(exist_ok=True)

        with open(output_path / "tokens.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tipo", "Valor", "Línea", "Columna"])
            for token in self.tokens:
                writer.writerow([token.type, token.value, token.line, token.column])

        with open(output_path / "lexical_errors.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Mensaje", "Valor", "Línea", "Columna"])
            for err in self.errors:
                writer.writerow([err.message, err.value, err.line, err.column])
