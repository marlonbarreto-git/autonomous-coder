"""Tests for auto_coder.executor module."""

from auto_coder.executor import CodeExecutor
from auto_coder.models import TestResult


class TestRunTests:
    def setup_method(self):
        self.executor = CodeExecutor()

    def test_run_tests_passing(self):
        source = "def add(a, b): return a + b"
        test_code = "from solution import add\n\ndef test_add():\n    assert add(1, 2) == 3"
        result = self.executor.run_tests(test_code, source)
        assert isinstance(result, TestResult)
        assert result.passed is True
        assert result.num_passed >= 1
        assert result.num_failed == 0

    def test_run_tests_failing(self):
        source = "def add(a, b): return a - b"  # wrong implementation
        test_code = "from solution import add\n\ndef test_add():\n    assert add(1, 2) == 3"
        result = self.executor.run_tests(test_code, source)
        assert result.passed is False
        assert result.num_failed > 0

    def test_run_tests_syntax_error(self):
        source = "def add(a, b) return a + b"  # missing colon
        test_code = "from solution import add\n\ndef test_add():\n    assert add(1, 2) == 3"
        result = self.executor.run_tests(test_code, source)
        assert result.passed is False


class TestRunCode:
    def setup_method(self):
        self.executor = CodeExecutor()

    def test_run_code_simple(self):
        stdout, stderr, returncode = self.executor.run_code("print('hello')")
        assert "hello" in stdout
        assert returncode == 0

    def test_run_code_error(self):
        stdout, stderr, returncode = self.executor.run_code("1/0")
        assert returncode != 0

    def test_run_code_timeout(self):
        stdout, stderr, returncode = self.executor.run_code("import time; time.sleep(30)")
        assert "timed out" in stderr.lower() or "timeout" in stderr.lower()
        assert returncode != 0
