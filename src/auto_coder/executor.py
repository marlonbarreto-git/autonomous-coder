import os
import subprocess
import sys
import tempfile

from auto_coder.models import TestResult


class CodeExecutor:
    def run_tests(self, test_code: str, source_code: str) -> TestResult:
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
                    timeout=30,
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
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Execution timed out", 1
