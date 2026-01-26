"""Data models for the Code Agent Benchmark Evaluator."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl


class EvalRequest(BaseModel):
    """Request model for starting a benchmark evaluation."""

    participants: Dict[str, HttpUrl]
    config: Dict[str, Any]


class TaskResult(BaseModel):
    """Model representing the result of a single benchmark task."""

    task_id: str
    task_title: str
    score: float
    passed: bool
    generated_code: Optional[str] = None
    details: Dict[str, Any]


class BenchmarkResult(BaseModel):
    """Model representing the overall results of a benchmark run."""

    total_tasks: int
    tasks_passed: int
    tasks_failed: int
    average_score: float
    task_results: List[TaskResult]
