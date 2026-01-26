"""Core orchestration logic for the Code Agent Benchmark."""

import logging
from typing import List, Dict, Any
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState
from a2a.utils import new_agent_text_message

from components.reporter import BenchmarkReporter
from models import TaskResult, BenchmarkResult

logger = logging.getLogger("benchmark_orchestrator")


class BenchmarkOrchestrator:
    """Orchestrates the benchmark execution loop."""

    def __init__(
        self,
        evaluator_map: Dict[str, Any],
        messenger: Any,
        task_loader: Any,
        bigcodebench_loader: Any,
    ):
        self.evaluators = evaluator_map
        self.messenger = messenger
        self.task_loader = task_loader
        self.bigcodebench_loader = bigcodebench_loader
        self.reporter = BenchmarkReporter()

    def _clean_code_submission(self, submission: str) -> str:
        """Remove markdown code blocks and extra formatting from submission."""
        lines = submission.strip().split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()

    async def run_benchmark(
        self,
        request_config: Dict[str, Any],
        participants: Dict[str, str],
        updater: TaskUpdater,
    ) -> Any:
        """Run the full benchmark suite based on request config."""
        source = request_config.get("source", "bigcodebench")
        category = request_config.get("category", "code_generation")
        num_tasks = request_config.get("num_tasks", 5)
        difficulty = request_config.get("difficulty")
        stdlib_only = request_config.get("stdlib_only", True)
        agent_url = participants["code_agent"]

        # Load tasks
        if source == "bigcodebench":
            from utils.stdlib_filter import filter_stdlib_tasks

            all_tasks = self.bigcodebench_loader.load_tasks(limit=None)
            tasks = filter_stdlib_tasks(all_tasks) if stdlib_only else all_tasks
            if difficulty:
                tasks = [t for t in tasks if t["difficulty"] == difficulty]
            tasks = tasks[:num_tasks]
        else:
            tasks = self.task_loader.load_tasks_by_category(
                category=category, difficulty=difficulty, limit=num_tasks
            )

        if not tasks:
            raise ValueError(f"No tasks found for source {source}")

        await updater.update_status(
            TaskState.working,
            new_agent_text_message(f"Loaded {len(tasks)} tasks. Starting evaluation."),
        )

        task_results = []
        evaluator = self.evaluators[category]

        for idx, task in enumerate(tasks, 1):
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    f"[{idx}/{len(tasks)}] Running task: {task['title']}"
                ),
            )

            prompt = task["prompt"]
            task_description = f"""You are solving a coding task. Please provide ONLY the Python code for the function requested.

Task: {task['title']}
Description: {task['description']}

{prompt}

Important: Return ONLY the complete Python code, including imports if needed. Do not include explanations or markdown formatting."""

            try:
                submission = await self.messenger.talk_to_agent(
                    task_description, agent_url
                )
                submission = self._clean_code_submission(submission)

                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(
                        f"[{idx}/{len(tasks)}] Received submission, evaluating..."
                    ),
                )

                # No more circularity, safe to import at top level if needed, but keeping here for scope
                eval_result = await evaluator.evaluate(task, submission)

                task_result = TaskResult(
                    task_id=task["id"],
                    task_title=task["title"],
                    score=eval_result["score"],
                    passed=eval_result["passed"],
                    generated_code=submission,
                    details=eval_result["details"],
                )
                task_results.append(task_result)

            except Exception as e:
                logger.error(f"Error evaluating task {task['id']}: {e}")
                task_result = TaskResult(
                    task_id=task["id"],
                    task_title=task["title"],
                    score=0.0,
                    passed=False,
                    details={"error": str(e)},
                )
                task_results.append(task_result)

        # Compute final results
        tasks_passed = sum(1 for r in task_results if r.passed)
        average_score = (
            sum(r.score for r in task_results) / len(task_results)
            if task_results
            else 0.0
        )

        benchmark_result = BenchmarkResult(
            total_tasks=len(task_results),
            tasks_passed=tasks_passed,
            tasks_failed=len(task_results) - tasks_passed,
            average_score=average_score,
            task_results=task_results,
        )

        summary = self.reporter.generate_summary(benchmark_result)
        await updater.update_status(TaskState.working, new_agent_text_message(summary))
        await self.reporter.add_artifacts(updater, benchmark_result, summary)

        return benchmark_result
