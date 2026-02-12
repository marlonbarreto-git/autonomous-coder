from dataclasses import dataclass, field
from enum import Enum


class StepType(Enum):
    GENERATE = "generate"
    TEST = "test"
    FIX = "fix"


@dataclass
class CodeFile:
    path: str
    content: str


@dataclass
class TestResult:
    passed: bool
    output: str
    num_passed: int = 0
    num_failed: int = 0


@dataclass
class CodingStep:
    step_type: StepType
    files: list[CodeFile] = field(default_factory=list)
    test_result: TestResult | None = None
    error_message: str = ""


@dataclass
class CodingTask:
    description: str
    steps: list[CodingStep] = field(default_factory=list)
    final_files: list[CodeFile] = field(default_factory=list)
    success: bool = False
    iterations: int = 0
