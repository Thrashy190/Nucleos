from models.symbol import Symbol
from models.syntax_error import SyntaxError
from models.ast_node import ASTNode

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = []
        self.errors = []

    def analyze(self, node: ASTNode, scope="global"):
        if node.type == "DECLARACIONES":
            for tipo in node.children:
                var_type = tipo.value
                for var in tipo.children:
                    name = var.value
                    if self.lookup(name, scope):
                        self.errors.append(SyntaxError("Variable ya declarada", name, -1, -1))
                    else:
                        self.symbol_table.append(Symbol(name=name, type=var_type, scope=scope))
        elif node.type == "ASIGNACION":
            var_node = node.children[0]
            value_node = node.children[1].children[0]
            symbol = self.lookup(var_node.value, scope)
            if not symbol:
                self.errors.append(SyntaxError("Variable no declarada", var_node.value, -1, -1))
            else:
                # Validación de tipo simple por tipo de valor
                if value_node.type == "LITERAL":
                    val = value_node.value
                    if val.replace(".", "", 1).isdigit():  # numérico
                        expected = "entero" if "." not in val else "real"
                    elif val in {"true", "false"}:
                        expected = "logico"
                    elif val.startswith('"'):
                        expected = "cadena"
                    else:
                        expected = None  # Puede ser otro ID

                    if expected and symbol.type != expected:
                        self.errors.append(SyntaxError(f"Asignación incompatible: se esperaba tipo {symbol.type}", val, -1, -1))
        elif node.type in {"LEER", "ESCRIBIR"}:
            var_node = node.children[0]
            if var_node.type == "ID":
                symbol = self.lookup(var_node.value, scope)
                if not symbol:
                    self.errors.append(SyntaxError("Variable no declarada", var_node.value, -1, -1))
        elif node.children:
            for child in node.children:
                self.analyze(child, scope)

    def lookup(self, name, scope):
        for s in self.symbol_table:
            if s.name == name and s.scope == scope:
                return s
        return None

    def export_symbol_table(self, path="output/symbol_table.csv"):
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre", "Tipo", "Ámbito", "Valor"])
            for s in self.symbol_table:
                writer.writerow([s.name, s.type, s.scope, s.value if s.value else ""])
