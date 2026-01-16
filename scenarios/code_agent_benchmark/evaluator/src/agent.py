"""Green agent for code agent benchmark evaluation."""

import logging
import os
from typing import Any
from pathlib import Path

from pydantic import BaseModel, HttpUrl, ValidationError

from a2a.server.tasks import TaskUpdater
from a2a.types import DataPart, Message, Part, TaskState, TextPart
from a2a.utils import get_message_text, new_agent_text_message

from messenger import Messenger
from utils.task_loader import TaskLoader
from utils.bigcodebench_loader import BigCodeBenchLoader
from utils.stdlib_filter import filter_stdlib_tasks
from evaluators.code_gen_evaluator import CodeGenerationEvaluator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code_benchmark_evaluator")


class EvalRequest(BaseModel):
    participants: dict[str, HttpUrl]
    config: dict[str, Any]


class TaskResult(BaseModel):
    task_id: str
    task_title: str
    score: float
    passed: bool
    details: dict[str, Any]


class BenchmarkResult(BaseModel):
    total_tasks: int
    tasks_passed: int
    tasks_failed: int
    average_score: float
    task_results: list[TaskResult]


class Agent:
    """Green agent that orchestrates code generation benchmark."""

    required_roles: list[str] = ["code_agent"]
    required_config_keys: list[str] = []  # category is optional if source is specified

    def __init__(self):
        self.messenger = Messenger()

        # Determine tasks directory for JSON tasks
        script_dir = Path(__file__).parent
        tasks_dir = script_dir.parent.parent / "tasks"
        self.task_loader = TaskLoader(str(tasks_dir))

        # Initialize BigCodeBench loader
        self.bigcodebench_loader = BigCodeBenchLoader()

        # Initialize evaluators
        self.evaluators = {"code_generation": CodeGenerationEvaluator()}

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        """Validate the evaluation request."""
        missing_roles = set(self.required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"

        missing_config_keys = set(self.required_config_keys) - set(
            request.config.keys()
        )
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"

        category = request.config.get("category")
        if category not in self.evaluators:
            return (
                False,
                f"Unsupported category: {category}. Supported: {list(self.evaluators.keys())}",
            )

        return True, "ok"

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Main execution loop for benchmark evaluation."""
        input_text = get_message_text(message)

        try:
            request = EvalRequest.model_validate_json(input_text)
            ok, validation_msg = self.validate_request(request)
            if not ok:
                await updater.reject(new_agent_text_message(validation_msg))
                return
        except ValidationError as e:
            await updater.reject(new_agent_text_message(f"Invalid request: {e}"))
            return

        await updater.update_status(
            TaskState.working,
            new_agent_text_message(
                f"Starting code agent benchmark.\\n{request.model_dump_json()}"
            ),
        )

        try:
            # Extract config
            source = request.config.get("source", "local")  # "local" or "bigcodebench"
            category = request.config.get("category", "code_generation")
            num_tasks = request.config.get("num_tasks", 5)
            difficulty = request.config.get("difficulty")
            stdlib_only = request.config.get("stdlib_only", True)  # For BigCodeBench
            agent_url = str(request.participants["code_agent"])

            # Load tasks based on source
            logger.info(f"Loading {num_tasks} tasks from source '{source}'")

            if source == "bigcodebench":
                # Load from BigCodeBench
                logger.info("Loading tasks from BigCodeBench dataset")
                all_tasks = self.bigcodebench_loader.load_tasks(limit=None)

                # Filter to stdlib only if requested
                if stdlib_only:
                    tasks = filter_stdlib_tasks(all_tasks)
                    logger.info(f"Filtered to {len(tasks)} stdlib-only tasks")
                else:
                    tasks = all_tasks

                # Apply difficulty filter if specified
                if difficulty:
                    tasks = [t for t in tasks if t["difficulty"] == difficulty]
                    logger.info(f"Filtered to {len(tasks)} {difficulty} tasks")

                # Limit number of tasks
                tasks = tasks[:num_tasks]
            else:
                # Load from local JSON files
                tasks = self.task_loader.load_tasks_by_category(
                    category=category, difficulty=difficulty, limit=num_tasks
                )

            if not tasks:
                await updater.failed(
                    new_agent_text_message(f"No tasks found for category '{category}'")
                )
                return

            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    f"Loaded {len(tasks)} tasks. Starting evaluation."
                ),
            )

            # Evaluate each task
            task_results = []
            evaluator = self.evaluators[category]

            for idx, task in enumerate(tasks, 1):
                logger.info(f"Evaluating task {idx}/{len(tasks)}: {task['id']}")

                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(
                        f"[{idx}/{len(tasks)}] Running task: {task['title']}"
                    ),
                )

                # Send task to agent
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

                    # Clean up submission (remove markdown code blocks if present)
                    submission = self._clean_code_submission(submission)

                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            f"[{idx}/{len(tasks)}] Received submission, evaluating..."
                        ),
                    )

                    # Evaluate submission
                    eval_result = await evaluator.evaluate(task, submission)

                    task_result = TaskResult(
                        task_id=task["id"],
                        task_title=task["title"],
                        score=eval_result["score"],
                        passed=eval_result["passed"],
                        details=eval_result["details"],
                    )
                    task_results.append(task_result)

                    status = "✓ PASSED" if eval_result["passed"] else "✗ FAILED"
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            f"[{idx}/{len(tasks)}] {status} - Score: {eval_result['score']:.2f}"
                        ),
                    )

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

                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            f"[{idx}/{len(tasks)}] ✗ ERROR - {str(e)}"
                        ),
                    )

            # Compute final results
            tasks_passed = sum(1 for r in task_results if r.passed)
            tasks_failed = len(task_results) - tasks_passed
            average_score = (
                sum(r.score for r in task_results) / len(task_results)
                if task_results
                else 0.0
            )

            benchmark_result = BenchmarkResult(
                total_tasks=len(task_results),
                tasks_passed=tasks_passed,
                tasks_failed=tasks_failed,
                average_score=average_score,
                task_results=task_results,
            )

            # Create summary message
            summary = f"""
Benchmark Complete!

Results:
- Total Tasks: {benchmark_result.total_tasks}
- Passed: {benchmark_result.tasks_passed}
- Failed: {benchmark_result.tasks_failed}
- Average Score: {benchmark_result.average_score:.2%}

Task Breakdown:
"""
            for result in task_results:
                status = "✓" if result.passed else "✗"
                summary += f"\\n{status} {result.task_title}: {result.score:.2%}"

            await updater.update_status(
                TaskState.working,
                new_agent_text_message(summary),
            )

            # Add artifacts
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=summary)),
                    Part(root=DataPart(data=benchmark_result.model_dump())),
                ],
                name="Benchmark Results",
            )

        finally:
            self.messenger.reset()

    def _clean_code_submission(self, submission: str) -> str:
        """Remove markdown code blocks and extra formatting from submission."""
        lines = submission.strip().split("\\n")

        # Remove markdown code block markers
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        return "\\n".join(lines).strip()
