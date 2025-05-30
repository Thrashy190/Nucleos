from models.vci_instruction import VCIInstruction
from models.ast_node import ASTNode

class VCIGenerator:
    def _init_(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def generate(self, node: ASTNode):
        if node is None:
            return

        if node.type == "PROGRAMA":
            # Procesar todo el programa
            for child in node.children:
                self.generate(child)

        elif node.type == "DECLARACIONES":
            # Las declaraciones no generan código intermedio directamente
            pass

        elif node.type == "BLOQUE":
            # Procesar todas las instrucciones del bloque
            for child in node.children:
                self.generate(child)

        elif node.type == "INSTRUCCIONES":
            # Procesar cada instrucción
            for child in node.children:
                self.generate(child)

        elif node.type == "LEER":
            # Generar instrucción de lectura
            var = node.children[0].value
            self.instructions.append(VCIInstruction("READ", "", "", var))

        elif node.type == "ESCRIBIR":
            # Generar instrucción de escritura
            expr = self.evaluate_expr(node.children[0].children[0])
            self.instructions.append(VCIInstruction("WRITE", expr, "", ""))

        elif node.type == "ASIGNACION":
            target = node.children[0].value
            value_expr = node.children[1]
            result = self.evaluate_expr(value_expr.children[0])
            self.instructions.append(VCIInstruction("=", result, "", target))

        elif node.type == "LEER":
            var = node.children[0].value
            self.instructions.append(VCIInstruction("LEER", "", "", var))

        elif node.type == "ESCRIBIR":
            val = self.evaluate_expr(node.children[0].children[0])
            self.instructions.append(VCIInstruction("ESCRIBIR", val, "", ""))

        elif node.type == "SI":
            cond = self.evaluate_expr(node.children[0].children[0])
            label_else = self.new_label()
            label_end = self.new_label()
            self.instructions.append(VCIInstruction("IF_FALSE", cond, "", f"GOTO {label_else}"))
            
            # Generar código para el bloque SI
            self.generate(node.children[1])  # BLOQUE_SI
            if len(node.children) == 3:
                self.instructions.append(VCIInstruction("GOTO", "", "", label_end))
                self.instructions.append(VCIInstruction("LABEL", "", "", label_else))
                self.generate(node.children[2])  # BLOQUE_SINO
                self.instructions.append(VCIInstruction("LABEL", "", "", label_end))
            else:
                self.instructions.append(VCIInstruction("LABEL", "", "", label_else))

        elif node.type == "MIENTRAS":
            label_start = self.new_label()
            label_end = self.new_label()
            self.instructions.append(VCIInstruction("LABEL", "", "", label_start))
            
            # Evaluar condición
            cond = self.evaluate_expr(node.children[0].children[0])
            self.instructions.append(VCIInstruction("IF_FALSE", cond, "", f"GOTO {label_end}"))
            self.generate(node.children[1])  # CUERPO
            self.instructions.append(VCIInstruction("GOTO", "", "", label_start))
            self.instructions.append(VCIInstruction("LABEL", "", "", label_end))

        elif node.type == "REPETIR":
            label_start = self.new_label()
            
            # Etiqueta de inicio
            self.instructions.append(VCIInstruction("LABEL", "", "", label_start))
            self.generate(node.children[0])  # CUERPO
            cond = self.evaluate_expr(node.children[1].children[0])
            self.instructions.append(VCIInstruction("IF_FALSE", cond, "", f"GOTO {label_start}"))

        elif node.type in {"INSTRUCCIONES", "BLOQUE", "BLOQUE_SI", "BLOQUE_SINO", "CUERPO", "PROGRAMA"}:
            for child in node.children:
                self.generate(child)

    def evaluate_expr(self, node: ASTNode):
        if node is None:
            return "?"

        if node.type == "LITERAL":
            return node.value
        elif node.type == "ID":
            return node.value
        elif node.type in {"OPERACION", "COMPARACION"}:
            left = self.evaluate_expr(node.children[0])
            right = self.evaluate_expr(node.children[1])
            temp = self.new_temp()
            
            # Manejar diferentes tipos de operaciones
            if node.value in {"+", "-", "*", "/"}:
                # Operaciones aritméticas
                self.instructions.append(VCIInstruction(node.value, left, right, temp))
            elif node.value in {"&&", "||"}:
                # Operaciones lógicas
                self.instructions.append(VCIInstruction(node.value, left, right, temp))
            elif node.value in {">", "<", ">=", "<=", "==", "!="}:
                # Comparaciones
                self.instructions.append(VCIInstruction(node.value, left, right, temp))
            
            return temp
        elif node.type == "VALOR":
            return self.evaluate_expr(node.children[0])
        elif node.type == "EXPR":
            return self.evaluate_expr(node.children[0])
        return "?"

    def new_temp(self):
        t = f"t{self.temp_count}"
        self.temp_count += 1
        return t

    def new_label(self):
        l = f"L{self.label_count}"
        self.label_count += 1
        return l

    def export_to_csv(self, path="output/vci.csv"):
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Operación", "Arg1", "Arg2", "Resultado"])
            for i in self.instructions:
                writer.writerow([i.operation, i.arg1, i.arg2, i.result])

    def print_ast_debug(self, node, indent=0):
        print("  " * indent + f"{node.type}: {node.value}")
        for child in node.children:
            self.print_ast_debug(child, indent + 1)
