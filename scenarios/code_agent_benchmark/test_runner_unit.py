"""Test the test runner utility."""

import sys
from pathlib import Path

# Add evaluator src to path
sys.path.insert(0, str(Path(__file__).parent / "evaluator" / "src"))

from utils.test_runner import TestRunner


def test_correct_solution():
    """Test that correct code passes tests."""
    runner = TestRunner()

    code = """
def add(a, b):
    return a + b
"""

    test_code = """
def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
    assert add(-1, 1) == 0
"""

    result = runner.run_tests(code, test_code)

    print("Test: Correct Solution")
    print(f"  Passed: {result['passed']}")
    print(f"  Num Passed: {result['num_passed']}")
    print(f"  Num Failed: {result['num_failed']}")

    assert result["passed"] == True, "Correct solution should pass"
    assert result["num_passed"] == 1, "Should have 1 passing test"
    assert result["num_failed"] == 0, "Should have 0 failing tests"

    print("  ✓ Test passed!")
    return True


def test_incorrect_solution():
    """Test that incorrect code fails tests."""
    runner = TestRunner()

    code = """
def add(a, b):
    return a - b  # Wrong!
"""

    test_code = """
def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
"""

    result = runner.run_tests(code, test_code)

    print("\\nTest: Incorrect Solution")
    print(f"  Passed: {result['passed']}")
    print(f"  Num Passed: {result['num_passed']}")
    print(f"  Num Failed: {result['num_failed']}")

    assert result["passed"] == False, "Incorrect solution should fail"
    assert result["num_failed"] > 0, "Should have failing tests"

    print("  ✓ Test passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Test Runner - Unit Tests")
    print("=" * 60)
    print()

    try:
        test_correct_solution()
        test_incorrect_solution()
        print()
        print("=" * 60)
        print("✓ ALL UNIT TESTS PASSED!")
        print("=" * 60)
    except Exception as e:
        print(f"\\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
