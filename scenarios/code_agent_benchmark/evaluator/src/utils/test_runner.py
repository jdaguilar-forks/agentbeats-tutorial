"""Test runner utility for executing Python code tests."""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any


class TestRunner:
    """Executes Python code and runs tests in isolated environment."""

    def __init__(self):
        self.timeout = 60

    def run_tests(self, code: str, test_code: str) -> Dict[str, Any]:
        """
        Run tests against provided code.

        Args:
            code: The Python code to test
            test_code: The test code (pytest format)

        Returns:
            Dictionary with test results including:
            - passed: bool
            - num_passed: int
            - num_failed: int
            - errors: list of error messages
            - output: stdout/stderr
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Write code to file
            code_file = tmpdir_path / "solution.py"
            code_file.write_text(code)

            # Write test to file
            test_file = tmpdir_path / "test_solution.py"
            test_content = f"""import sys
sys.path.insert(0, '{tmpdir}')
from solution import *

{test_code}
"""
            test_file.write_text(test_content)

            # Run pytest
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir,
                )

                output = result.stdout + result.stderr
                passed = result.returncode == 0

                # Parse pytest output for counts
                num_passed = output.count(" PASSED")
                num_failed = output.count(" FAILED")

                errors = []
                if not passed:
                    # Extract error messages
                    lines = output.split("\n")
                    for i, line in enumerate(lines):
                        if "FAILED" in line or "ERROR" in line:
                            errors.append(line)

                return {
                    "passed": passed,
                    "num_passed": num_passed,
                    "num_failed": num_failed,
                    "errors": errors,
                    "output": output,
                }

            except subprocess.TimeoutExpired:
                return {
                    "passed": False,
                    "num_passed": 0,
                    "num_failed": -1,
                    "errors": [f"Test execution timed out after {self.timeout}s"],
                    "output": "",
                }
            except Exception as e:
                return {
                    "passed": False,
                    "num_passed": 0,
                    "num_failed": -1,
                    "errors": [f"Test execution error: {str(e)}"],
                    "output": "",
                }
