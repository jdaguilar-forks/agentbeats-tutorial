"""Code generation evaluator."""

import logging
from typing import Dict, Any
from pathlib import Path
from evaluators.base import BaseEvaluator
from utils.test_runner import TestRunner


logger = logging.getLogger("code_gen_evaluator")


class CodeGenerationEvaluator(BaseEvaluator):
    """Evaluator for code generation tasks."""

    def __init__(self):
        self.test_runner = TestRunner()

    async def evaluate(self, task: Dict[str, Any], submission: str) -> Dict[str, Any]:
        """
        Evaluate a code generation submission.

        Scoring:
        - 50%: Test pass rate
        - 30%: Code correctness (all tests pass)
        - 20%: Code quality (no obvious issues)
        """
        test_code = task.get("test_code", "")

        # Check if submission is a file path
        import os

        if os.path.exists(submission) and submission.endswith(".py"):
            logger.info(f"Reading code from file: {submission}")
            try:
                with open(submission, "r") as f:
                    code_content = f.read()
                logger.info(f"Read {len(code_content)} characters from file")
                submission = code_content
            except Exception as e:
                logger.error(f"Failed to read code from file {submission}: {e}")
                return {
                    "score": 0.0,
                    "passed": False,
                    "details": {
                        "tests_passed": 0,
                        "tests_failed": 0,
                        "test_pass_rate": 0.0,
                        "errors": [f"Failed to read code file: {e}"],
                        "test_output": f"File read error: {e}",
                    },
                }

        # Save debug artifacts
        try:
            debug_dir = Path("scenarios/code_agent_benchmark/debug")
            debug_dir.mkdir(exist_ok=True, parents=True)

            task_id = task["id"]
            # Save generated code
            with open(debug_dir / f"{task_id}_generated.py", "w") as f:
                f.write(submission)

            # Save test code
            with open(debug_dir / f"{task_id}_test.py", "w") as f:
                f.write(test_code)

            logger.info(f"Saved debug files to {debug_dir}")
        except Exception as e:
            logger.warning(f"Failed to save debug files: {e}")

        # Run tests
        logger.info(f"Running tests for task {task['id']}")
        test_results = self.test_runner.run_tests(submission, test_code)

        # Save test output
        try:
            with open(debug_dir / f"{task_id}_results.txt", "w") as f:
                f.write(test_results["output"])
        except Exception:
            pass

        # Calculate scores
        tests_passed = test_results["passed"]
        num_passed = test_results["num_passed"]
        num_failed = test_results["num_failed"]

        if num_passed + num_failed > 0:
            pass_rate = num_passed / (num_passed + num_failed)
        else:
            pass_rate = 0.0

        # Correctness score: 1.0 if all pass, otherwise proportional
        correctness_score = 1.0 if tests_passed else pass_rate

        # Quality score: simple heuristic for now
        quality_score = 1.0 if tests_passed else 0.5

        # Final score
        final_score = 0.50 * pass_rate + 0.30 * correctness_score + 0.20 * quality_score

        return {
            "score": final_score,
            "passed": tests_passed,
            "details": {
                "tests_passed": num_passed,
                "tests_failed": num_failed,
                "test_pass_rate": pass_rate,
                "errors": test_results["errors"],
                "test_output": test_results["output"],
            },
        }
