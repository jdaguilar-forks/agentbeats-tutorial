"""Green agent for code agent benchmark evaluation."""

import logging
import os
from typing import Any, List, Dict, Optional
from pathlib import Path

from pydantic import BaseModel, HttpUrl, ValidationError

from a2a.server.tasks import TaskUpdater
from a2a.types import DataPart, Message, Part, TaskState, TextPart
from a2a.utils import get_message_text, new_agent_text_message

from models import EvalRequest, TaskResult, BenchmarkResult
from messenger import Messenger
from utils.task_loader import TaskLoader
from utils.bigcodebench_loader import BigCodeBenchLoader
from evaluators.code_gen_evaluator import CodeGenerationEvaluator
from components.orchestrator import BenchmarkOrchestrator


logger = logging.getLogger("code_benchmark_evaluator")


class Agent:
    """Green agent that orchestrates code generation benchmark."""

    required_roles: List[str] = ["code_agent"]

    def __init__(self, model: str = None):
        self.model = model
        self.messenger = Messenger()

        # Loaders
        script_dir = Path(__file__).parent
        tasks_dir = script_dir.parent.parent / "tasks"
        self.task_loader = TaskLoader(str(tasks_dir))
        self.bigcodebench_loader = BigCodeBenchLoader()

        # Evaluators
        self.evaluators = {"code_generation": CodeGenerationEvaluator()}

        # Orchestrator
        self.orchestrator = BenchmarkOrchestrator(
            evaluator_map=self.evaluators,
            messenger=self.messenger,
            task_loader=self.task_loader,
            bigcodebench_loader=self.bigcodebench_loader,
        )

        if self.model:
            logger.info(f"Initialized evaluator with model: {self.model}")

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        """Validate the evaluation request."""
        missing_roles = set(self.required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"

        category = request.config.get("category", "code_generation")
        if category not in self.evaluators:
            return False, f"Unsupported category: {category}"

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
        except Exception as e:
            await updater.reject(new_agent_text_message(f"Invalid request: {e}"))
            return

        await updater.update_status(
            TaskState.working,
            new_agent_text_message(
                f"Starting code agent benchmark.\n{request.model_dump_json()}"
            ),
        )

        try:
            participants = {
                role: str(url) for role, url in request.participants.items()
            }
            await self.orchestrator.run_benchmark(request.config, participants, updater)
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            await updater.failed(new_agent_text_message(f"Benchmark failed: {e}"))
        finally:
            self.messenger.reset()
