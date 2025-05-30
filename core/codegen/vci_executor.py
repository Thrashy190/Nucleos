from models.vci_instruction import VCIInstruction

class VCIExecutor:
    def __init__(self, instructions):
        self.instructions = instructions
        self.stack = []
        self.labels = self._build_label_table()
        self.variables = {}
        self.ip = 0  # Instruction pointer
        self.output_steps = []
        self.execution_trace = []

    def _build_label_table(self):
        labels = {}
        for i, instr in enumerate(self.instructions):
            if isinstance(instr, VCIInstruction) and instr.operation == "LABEL":
                labels[instr.result] = i
        return labels

    def execute(self):
        while self.ip < len(self.instructions):
            instr = self.instructions[self.ip]
            op = instr.operation

            snapshot = {
                "Operación": instr.operation,
                "Arg1": instr.arg1,
                "Arg2": instr.arg2,
                "Resultado": instr.result,
                "Stack": list(self.stack),
                "Variables": dict(self.variables)
            }

            jumped = False

            if op == "=":
                val = self._get_value(instr.arg1)
                self.variables[instr.result] = val
                self.stack.append(val)

            elif op in {"+", "-", "*", "/"}:
                left = self._get_value(instr.arg1)
                right = self._get_value(instr.arg2)
                result = self._apply_operator(op, left, right)
                self.variables[instr.result] = result
                self.stack.append(result)

            elif op == "IF_FALSE":
                cond = self._get_value(instr.arg1)
                if not self._is_true(cond):
                    self.execution_trace.append(snapshot)
                    self.ip = self.labels.get(instr.result.split()[-1], self.ip)
                    jumped = True


            elif op == "GOTO":
                self.execution_trace.append(snapshot)
                self.ip = self.labels.get(instr.result, self.ip)
                jumped = True

            elif op == "LEER":
                val = input(f"Ingrese valor para {instr.result}: ")
                self.variables[instr.result] = self._get_value(val)

            elif op == "ESCRIBIR":
                val = self._get_value(instr.arg1)
                print(f"{instr.arg1} = {val}")

            elif op == "LABEL":
                pass  # Track only

            if not jumped:
                self.execution_trace.append(snapshot)
                self.ip += 1

    def _get_value(self, val):
        if val in self.variables:
            return self.variables[val]
        try:
            return float(val) if "." in val else int(val)
        except (ValueError, TypeError):
            return val

    def _is_true(self, val):
        return val not in ["false", False, 0, "0", None, ""]

    def _apply_operator(self, op, left, right):
        try:
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/": return left / right if right != 0 else 0
        except TypeError:
            return 0

    def export_execution_table(self, path):
        import csv
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Operación", "Arg1", "Arg2", "Resultado", "Stack", "Variables"])
            for step in self.execution_trace:
                writer.writerow([
                    step["Operación"],
                    step["Arg1"],
                    step["Arg2"],
                    step["Resultado"],
                    str(step["Stack"]),
                    str(step["Variables"])
                ])

    def export_variables(self, path):
        import csv
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Variable", "Valor"])
            for k, v in self.variables.items():
                writer.writerow([k, v])
