from dataclasses import dataclass
import io

@dataclass
class ModuleExecutionState:
    stdout: io.StringIO
    context: dict
