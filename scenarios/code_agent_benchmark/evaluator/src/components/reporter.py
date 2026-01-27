"""Reporting and artifact management for the Code Agent Benchmark."""

from a2a.server.tasks import TaskUpdater
from a2a.types import Part, TextPart, DataPart
from models import BenchmarkResult


class BenchmarkReporter:
    """Handles result formatting and artifact generation."""

    @staticmethod
    def generate_summary(benchmark_result: BenchmarkResult) -> str:
        """Create a human-readable summary of the benchmark results."""
        summary = f"""
Benchmark Complete!

Results:
- Total Tasks: {benchmark_result.total_tasks}
- Passed: {benchmark_result.tasks_passed}
- Failed: {benchmark_result.tasks_failed}
- Average Score: {benchmark_result.average_score:.2%}

Task Breakdown:
"""
        for result in benchmark_result.task_results:
            status = "✓" if result.passed else "✗"
            summary += f"\n{status} {result.task_title}: {result.score:.2%}"

        return summary

    @staticmethod
    async def add_artifacts(
        updater: TaskUpdater, benchmark_result: BenchmarkResult, summary: str
    ):
        """Add benchmark result artifacts to the task updater."""
        await updater.add_artifact(
            parts=[
                Part(root=TextPart(text=summary)),
                Part(root=DataPart(data=benchmark_result.model_dump())),
            ],
            name="Benchmark Results",
        )
