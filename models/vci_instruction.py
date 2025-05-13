from dataclasses import dataclass

@dataclass
class VCIInstruction:
    operation: str
    arg1: str = ""
    arg2: str = ""
    result: str = ""
