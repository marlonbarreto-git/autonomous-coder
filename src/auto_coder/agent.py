"""Autonomous coder agent loop - generates code, runs tests, fixes until green."""

from collections.abc import Callable

from auto_coder.executor import CodeExecutor
from auto_coder.models import CodeFile, CodingStep, CodingTask, StepType

DEFAULT_MAX_ITERATIONS: int = 5


class AutonomousCoder:
    """Agent that iteratively generates code, runs tests, and applies fixes."""

    def __init__(
        self,
        generate_fn: Callable[[str, str], str] | None = None,
        fix_fn: Callable[[str, str, str], str] | None = None,
        executor: CodeExecutor | None = None,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ) -> None:
        """Args:
            generate_fn: Callable that produces source code from a task
                description and test code.
            fix_fn: Callable that fixes source code given the task
                description, current code, and error output.
            executor: Test executor instance.
            max_iterations: Maximum generate-test-fix cycles before giving up.
        """
        self._generate_fn = generate_fn or self._default_generate
        self._fix_fn = fix_fn or self._default_fix
        self.executor = executor or CodeExecutor()
        self.max_iterations = max_iterations

    def solve(self, task_description: str, test_code: str) -> CodingTask:
        """Run the generate-test-fix loop until tests pass or iterations exhaust.

        Args:
            task_description: Natural-language description of the coding task.
            test_code: Pytest test source to validate the solution.

        Returns:
            A CodingTask recording all steps and the final outcome.
        """
        task = CodingTask(description=task_description)

        source_code = self._generate_fn(task_description, test_code)
        gen_step = CodingStep(
            step_type=StepType.GENERATE,
            files=[CodeFile(path="solution.py", content=source_code)],
        )
        task.steps.append(gen_step)

        for i in range(self.max_iterations):
            task.iterations = i + 1
            test_result = self.executor.run_tests(test_code, source_code)
            task.steps[-1].test_result = test_result

            if test_result.passed:
                task.success = True
                task.final_files = [CodeFile(path="solution.py", content=source_code)]
                return task

            source_code = self._fix_fn(task_description, source_code, test_result.output)
            fix_step = CodingStep(
                step_type=StepType.FIX,
                files=[CodeFile(path="solution.py", content=source_code)],
            )
            task.steps.append(fix_step)

        task.success = False
        return task

    @staticmethod
    def _default_generate(description: str, test_code: str) -> str:
        """Return a placeholder when no generation function is provided."""
        return "# Generated code placeholder"

    @staticmethod
    def _default_fix(description: str, code: str, error: str) -> str:
        """Return the code unchanged when no fix function is provided."""
        return code
