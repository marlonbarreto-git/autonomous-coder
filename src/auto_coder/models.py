"""Domain models for the autonomous coder agent."""

from dataclasses import dataclass, field
from enum import Enum


class StepType(Enum):
    """Types of steps the agent can perform during a coding task."""

    GENERATE = "generate"
    TEST = "test"
    FIX = "fix"


@dataclass
class CodeFile:
    """A source file with its path and content."""

    path: str
    content: str


@dataclass
class TestResult:
    """Outcome of running a test suite against generated code."""

    passed: bool
    output: str
    num_passed: int = 0
    num_failed: int = 0


@dataclass
class CodingStep:
    """A single step in the agent's generate-test-fix loop."""

    step_type: StepType
    files: list[CodeFile] = field(default_factory=list)
    test_result: TestResult | None = None
    error_message: str = ""


@dataclass
class CodingTask:
    """Full record of a coding task including all steps and final output."""

    description: str
    steps: list[CodingStep] = field(default_factory=list)
    final_files: list[CodeFile] = field(default_factory=list)
    success: bool = False
    iterations: int = 0
