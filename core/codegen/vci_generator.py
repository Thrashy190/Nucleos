from models.ast_node import ASTNode
from models.vci_instruction import VCIInstruction

class VCIGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def generate(self, node: ASTNode):
        if node.type == "ASIGNACION":
            target = node.children[0].value
            expr = node.children[1].children[0]
            result = self.evaluate_expr(expr)
            self.instructions.append(VCIInstruction("=", result, "", target))

        elif node.type == "SI":
            cond = self.evaluate_expr(node.children[0].children[0])
            label_else = self.new_label()
            label_end = self.new_label()

            self.instructions.append(VCIInstruction("IF_FALSE", cond, "", f"GOTO {label_else}"))
            self.generate(node.children[1])  # BLOQUE_SI
            if len(node.children) == 3:  # si tiene un BLOQUE_SINO
                self.instructions.append(VCIInstruction("GOTO", "", "", f"{label_end}"))
                self.instructions.append(VCIInstruction("LABEL", "", "", label_else))
                self.generate(node.children[2])
                self.instructions.append(VCIInstruction("LABEL", "", "", label_end))
            else:
                self.instructions.append(VCIInstruction("LABEL", "", "", label_else))

        elif node.type == "MIENTRAS":
            label_start = self.new_label()
            label_end = self.new_label()

            self.instructions.append(VCIInstruction("LABEL", "", "", label_start))
            cond = self.evaluate_expr(node.children[0].children[0])
            self.instructions.append(VCIInstruction("IF_FALSE", cond, "", f"GOTO {label_end}"))
            self.generate(node.children[1])  # cuerpo
            self.instructions.append(VCIInstruction("GOTO", "", "", label_start))
            self.instructions.append(VCIInstruction("LABEL", "", "", label_end))

        elif node.type == "REPETIR":
            label_start = self.new_label()
            self.instructions.append(VCIInstruction("LABEL", "", "", label_start))
            self.generate(node.children[0])  # cuerpo
            cond = self.evaluate_expr(node.children[1].children[0])
            self.instructions.append(VCIInstruction("IF_FALSE", cond, "", f"GOTO {label_start}"))

        elif node.type in {"INSTRUCCIONES", "BLOQUE"}:
            for child in node.children:
                self.generate(child)

    def evaluate_expr(self, node: ASTNode):
        if node.type == "LITERAL":
            return node.value
        elif node.type in {"OPERACION", "COMPARACION"}:
            left = self.evaluate_expr(node.children[0])
            right = self.evaluate_expr(node.children[1])
            temp = self.new_temp()
            self.instructions.append(VCIInstruction(node.value, left, right, temp))
            return temp
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
