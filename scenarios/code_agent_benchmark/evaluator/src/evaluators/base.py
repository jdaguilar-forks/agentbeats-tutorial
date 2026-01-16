"""Base evaluator class for code tasks."""

from typing import Dict, Any
from abc import ABC, abstractmethod


class BaseEvaluator(ABC):
    """Base class for task evaluators."""

    @abstractmethod
    async def evaluate(self, task: Dict[str, Any], submission: str) -> Dict[str, Any]:
        """
        Evaluate a code submission for a task.

        Args:
            task: Task definition dictionary
            submission: Code submitted by the agent

        Returns:
            Evaluation results dictionary with:
            - score: float (0.0 to 1.0)
            - passed: bool
            - details: dict with detailed metrics
        """
        pass
