"""Purple agent for solving coding tasks."""

import logging
import os
from dotenv import load_dotenv

from litellm import completion

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState
from a2a.utils import get_message_text, new_agent_text_message


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code_agent")


class Agent:
    """Purple agent that solves coding tasks using an LLM."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        logger.info(f"Initialized code agent with model: {model}")

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Solve a coding task."""
        task_description = get_message_text(message)

        await updater.update_status(
            TaskState.working,
            new_agent_text_message("Analyzing task..."),
        )

        try:
            # Use LLM to generate code
            logger.info("Generating code solution...")

            system_prompt = """You are an expert Python programmer. You will be given a coding task with a function signature and description.
Your job is to implement the function correctly.

IMPORTANT: Return ONLY the Python code. Do not include markdown formatting, explanations, or any other text.
Include all necessary imports at the top of your response."""

            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task_description},
                ],
                temperature=0.2,
            )

            code_solution = response.choices[0].message.content.strip()

            await updater.update_status(
                TaskState.working,
                new_agent_text_message("Code solution generated. Submitting..."),
            )

            # Return the solution
            await updater.complete(new_agent_text_message(code_solution))

        except Exception as e:
            logger.error(f"Error generating code: {e}")
            await updater.failed(
                new_agent_text_message(f"Failed to generate code: {e}")
            )
