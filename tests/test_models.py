"""Tests for auto_coder.models module."""

from auto_coder.models import CodeFile, CodingStep, CodingTask, StepType, TestResult


class TestStepTypeEnum:
    def test_step_type_values(self):
        assert StepType.GENERATE.value == "generate"
        assert StepType.TEST.value == "test"
        assert StepType.FIX.value == "fix"

    def test_step_type_members(self):
        assert set(StepType.__members__.keys()) == {"GENERATE", "TEST", "FIX"}


class TestCodeFile:
    def test_code_file_creation(self):
        cf = CodeFile(path="main.py", content="print('hi')")
        assert cf.path == "main.py"
        assert cf.content == "print('hi')"


class TestTestResult:
    def test_test_result_defaults(self):
        tr = TestResult(passed=True, output="ok")
        assert tr.passed is True
        assert tr.output == "ok"
        assert tr.num_passed == 0
        assert tr.num_failed == 0

    def test_test_result_with_counts(self):
        tr = TestResult(passed=False, output="fail", num_passed=2, num_failed=1)
        assert tr.num_passed == 2
        assert tr.num_failed == 1


class TestCodingStep:
    def test_coding_step_creation(self):
        step = CodingStep(step_type=StepType.GENERATE)
        assert step.step_type == StepType.GENERATE
        assert step.files == []
        assert step.test_result is None
        assert step.error_message == ""

    def test_coding_step_with_files(self):
        f = CodeFile(path="a.py", content="x=1")
        step = CodingStep(step_type=StepType.FIX, files=[f])
        assert len(step.files) == 1
        assert step.files[0].path == "a.py"


class TestCodingTask:
    def test_coding_task_defaults(self):
        task = CodingTask(description="Build something")
        assert task.description == "Build something"
        assert task.steps == []
        assert task.final_files == []
        assert task.success is False
        assert task.iterations == 0
