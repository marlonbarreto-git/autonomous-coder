"""Sandboxed code execution and test runner."""

import os
import subprocess
import sys
import tempfile

from auto_coder.models import TestResult

TEST_TIMEOUT_SECONDS: int = 30
CODE_TIMEOUT_SECONDS: int = 10


class CodeExecutor:
    """Runs generated code and test suites in isolated temp directories."""

    def run_tests(self, test_code: str, source_code: str) -> TestResult:
        """Execute a pytest suite against the given source code.

        Args:
            test_code: Pytest test source code.
            source_code: The solution code under test.

        Returns:
            A TestResult with pass/fail status and output details.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = os.path.join(tmpdir, "solution.py")
            with open(src_path, "w") as f:
                f.write(source_code)

            test_path = os.path.join(tmpdir, "test_solution.py")
            test_content = f"import sys; sys.path.insert(0, '{tmpdir}')\n{test_code}"
            with open(test_path, "w") as f:
                f.write(test_content)

            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=TEST_TIMEOUT_SECONDS,
                    cwd=tmpdir,
                )
                output = result.stdout + result.stderr
                passed = result.returncode == 0
                num_passed = output.count(" PASSED")
                num_failed = output.count(" FAILED")
                return TestResult(
                    passed=passed, output=output, num_passed=num_passed, num_failed=num_failed
                )
            except subprocess.TimeoutExpired:
                return TestResult(passed=False, output="Test execution timed out")

    def run_code(self, code: str) -> tuple[str, str, int]:
        """Execute arbitrary Python code and return its output.

        Args:
            code: Python source code to execute.

        Returns:
            A tuple of (stdout, stderr, return_code).
        """
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=CODE_TIMEOUT_SECONDS,
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Execution timed out", 1
