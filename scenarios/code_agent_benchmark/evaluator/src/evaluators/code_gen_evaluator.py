"""Code generation evaluator."""

import logging
from typing import Dict, Any
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

        # Run tests
        logger.info(f"Running tests for task {task['id']}")
        test_results = self.test_runner.run_tests(submission, test_code)

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
