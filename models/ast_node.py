from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ASTNode:
    type: str
    value: Optional[str] = None
    children: List['ASTNode'] = field(default_factory=list)
