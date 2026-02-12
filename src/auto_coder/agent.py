"""Autonomous coder agent loop - generates code, runs tests, fixes until green."""

from auto_coder.executor import CodeExecutor
from auto_coder.models import CodeFile, CodingStep, CodingTask, StepType


class AutonomousCoder:
    def __init__(self, generate_fn=None, fix_fn=None, executor=None, max_iterations: int = 5):
        self._generate_fn = generate_fn or self._default_generate
        self._fix_fn = fix_fn or self._default_fix
        self.executor = executor or CodeExecutor()
        self.max_iterations = max_iterations

    def solve(self, task_description: str, test_code: str) -> CodingTask:
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
        return "# Generated code placeholder"

    @staticmethod
    def _default_fix(description: str, code: str, error: str) -> str:
        return code
