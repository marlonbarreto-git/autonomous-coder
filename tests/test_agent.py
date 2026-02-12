"""Tests for AutonomousCoder agent loop."""

from unittest.mock import MagicMock

import pytest

from auto_coder.agent import AutonomousCoder
from auto_coder.models import CodeFile, StepType, TestResult


@pytest.fixture
def passing_result():
    return TestResult(passed=True, output="All tests passed", num_passed=3, num_failed=0)


@pytest.fixture
def failing_result():
    return TestResult(passed=False, output="AssertionError: expected 4 got 0", num_passed=1, num_failed=2)


def _make_coder(generate_fn=None, fix_fn=None, executor=None, max_iterations=5):
    gen = generate_fn or MagicMock(return_value="def add(a, b): return a + b")
    fix = fix_fn or MagicMock(return_value="def add(a, b): return a + b")
    exc = executor or MagicMock()
    return AutonomousCoder(generate_fn=gen, fix_fn=fix, executor=exc, max_iterations=max_iterations)


class TestSolvePassesFirstTry:
    def test_success_and_iterations(self, passing_result):
        executor = MagicMock()
        executor.run_tests.return_value = passing_result
        gen_fn = MagicMock(return_value="def add(a, b): return a + b")

        coder = _make_coder(generate_fn=gen_fn, executor=executor)
        task = coder.solve("write add function", "def test_add(): assert add(2,2)==4")

        assert task.success is True
        assert task.iterations == 1
        assert len(task.steps) == 1
        assert task.steps[0].step_type == StepType.GENERATE


class TestSolveFixesOnFailure:
    def test_generates_then_fixes(self, failing_result, passing_result):
        executor = MagicMock()
        executor.run_tests.side_effect = [failing_result, passing_result]
        gen_fn = MagicMock(return_value="def add(a, b): return 0")
        fix_fn = MagicMock(return_value="def add(a, b): return a + b")

        coder = _make_coder(generate_fn=gen_fn, fix_fn=fix_fn, executor=executor)
        task = coder.solve("write add function", "def test_add(): assert add(2,2)==4")

        assert task.success is True
        gen_fn.assert_called_once()
        fix_fn.assert_called_once()


class TestSolveMaxIterationsReached:
    def test_fails_after_max_iterations(self, failing_result):
        executor = MagicMock()
        executor.run_tests.return_value = failing_result

        coder = _make_coder(executor=executor, max_iterations=2)
        task = coder.solve("write add function", "def test_add(): assert add(2,2)==4")

        assert task.success is False
        assert task.iterations == 2


class TestSolveGenerateFnReceivesDescription:
    def test_generate_called_with_correct_args(self, passing_result):
        executor = MagicMock()
        executor.run_tests.return_value = passing_result
        gen_fn = MagicMock(return_value="code")

        coder = _make_coder(generate_fn=gen_fn, executor=executor)
        desc = "implement fibonacci"
        test_code = "def test_fib(): assert fib(5)==5"
        coder.solve(desc, test_code)

        gen_fn.assert_called_once_with(desc, test_code)


class TestSolveFixFnReceivesError:
    def test_fix_called_with_error_output(self, failing_result, passing_result):
        executor = MagicMock()
        executor.run_tests.side_effect = [failing_result, passing_result]
        gen_fn = MagicMock(return_value="bad code")
        fix_fn = MagicMock(return_value="good code")

        coder = _make_coder(generate_fn=gen_fn, fix_fn=fix_fn, executor=executor)
        desc = "implement fibonacci"
        coder.solve(desc, "test code")

        fix_fn.assert_called_once_with(desc, "bad code", failing_result.output)


class TestSolveStepsTracked:
    def test_two_steps_on_one_fail_one_pass(self, failing_result, passing_result):
        executor = MagicMock()
        executor.run_tests.side_effect = [failing_result, passing_result]
        gen_fn = MagicMock(return_value="v1")
        fix_fn = MagicMock(return_value="v2")

        coder = _make_coder(generate_fn=gen_fn, fix_fn=fix_fn, executor=executor)
        task = coder.solve("task", "tests")

        assert len(task.steps) == 2
        assert task.steps[0].step_type == StepType.GENERATE
        assert task.steps[1].step_type == StepType.FIX


class TestSolveFinalFilesSetOnSuccess:
    def test_final_files_contain_passing_code(self, failing_result, passing_result):
        executor = MagicMock()
        executor.run_tests.side_effect = [failing_result, passing_result]
        gen_fn = MagicMock(return_value="v1")
        fix_fn = MagicMock(return_value="v2_fixed")

        coder = _make_coder(generate_fn=gen_fn, fix_fn=fix_fn, executor=executor)
        task = coder.solve("task", "tests")

        assert task.success is True
        assert len(task.final_files) == 1
        assert task.final_files[0].content == "v2_fixed"
        assert task.final_files[0].path == "solution.py"


class TestDefaultMaxIterations:
    def test_default_is_five(self):
        coder = AutonomousCoder()
        assert coder.max_iterations == 5
