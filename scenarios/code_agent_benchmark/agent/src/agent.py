"""Purple agent for solving coding tasks using Open Router."""

import logging
import os
import re
from dotenv import load_dotenv

from litellm import completion
import asyncio
import time

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState
from a2a.utils import get_message_text, new_agent_text_message

# Load environment variables
load_dotenv()

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code_agent")

# Configure litellm for Open Router
openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY", "")
if openrouter_api_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
else:
    logger.warning("OPEN_ROUTER_API_KEY not found in environment variables")

os.environ["LITELLM_DROP_PARAMS"] = "True"
os.environ["LITELLM_SET_VERBOSE"] = "True"


class Agent:
    """Purple agent that solves coding tasks using an LLM."""

    def __init__(self, model: str = "google/gemini-2.0-flash-exp:free"):
        self.model = model
        logger.info(f"Initialized code agent with model: {model}")

    def _clean_code(self, code: str) -> str:
        """Strip markdown markers and extra text."""
        # Find content inside ```python ... ``` or ``` ... ```
        match = re.search(r"```(?:python)?\n?(.*?)```", code, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: if no markers, try to find the start of code (imports or defs)
        lines = code.split("\n")
        cleaned_lines = []
        in_code = False
        for line in lines:
            if not in_code and (
                line.strip().startswith("import ")
                or line.strip().startswith("from ")
                or line.strip().startswith("def ")
            ):
                in_code = True
            if in_code:
                cleaned_lines.append(line)

        if cleaned_lines:
            return "\n".join(cleaned_lines).strip()

        return code.strip()

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Solve a coding task."""
        task_description = get_message_text(message)

        await updater.update_status(
            TaskState.working,
            new_agent_text_message("Analyzing task..."),
        )

        try:
            # Use LLM to generate code
            logger.info(f"Generating code solution with model: {self.model}")
            logger.info(f"Task description length: {len(task_description)} characters")

            system_prompt = """You are an expert Python programmer.
Your task is to provide ONLY raw Python code. 

RULES:
1. Do NOT use markdown code blocks (e.g., no ```python).
2. Do NOT provide any explanations, comments (unless inside the code), or conversational filler.
3. Provide ONLY the complete Python implementation including necessary imports.
4. Your response must be directly executable as a .py file.

Fail to follow these rules will break the evaluation system."""

            logger.info("Sending request to Open Router...")
            logger.info(f"Using model: {self.model}")
            logger.info(f"System prompt length: {len(system_prompt)}")
            logger.info(f"Task description: {task_description[:200]}...")

            max_retries = 3
            # Initialize with a default fallback to ensure file is never empty
            code_solution = (
                "def placeholder(): pass  # Error: Generation failed (Unknown error)"
            )

            for attempt in range(max_retries):
                try:
                    response = completion(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": task_description},
                        ],
                        temperature=0.2,
                        timeout=60,
                    )

                    logger.info(f"Response received: {response}")

                    if not response or not response.choices:
                        raise ValueError("Empty response from LLM")

                    content = response.choices[0].message.content.strip()
                    if len(content) == 0:
                        raise ValueError("Empty code content in response")

                    code_solution = content

                    # Success!
                    break

                except Exception as e:
                    logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")

                    # Update fallback with specific error
                    error_msg = str(e).replace("\n", " ")
                    code_solution = f"def placeholder(): pass  # Error: {error_msg}"

                    if attempt < max_retries - 1:
                        wait_time = 2**attempt
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error("All retries failed.")

            await updater.update_status(
                TaskState.working,
                new_agent_text_message("Code solution generated. Writing to file..."),
            )

            # Write code solution to a temporary file
            import tempfile
            import os
            import uuid

            # Create a unique filename for this task
            task_id = str(uuid.uuid4())
            temp_dir = tempfile.gettempdir()
            code_filename = f"code_solution_{task_id}.py"
            code_filepath = os.path.join(temp_dir, code_filename)

            try:
                # Clean code solution before writing (removes markdown blocks)
                cleaned_code = self._clean_code(code_solution)
                with open(code_filepath, "w") as f:
                    f.write(cleaned_code)
                logger.info(f"Code solution written to: {code_filepath}")

                # Return the file path instead of the code
                await updater.complete(new_agent_text_message(code_filepath))

            except Exception as e:
                logger.error(f"Failed to write code to file: {e}")
                await updater.failed(
                    new_agent_text_message(
                        f"Failed to write code solution to file: {e}"
                    )
                )

        except Exception as e:
            logger.error(f"Error generating code: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            await updater.failed(
                new_agent_text_message(f"Failed to generate code: {e}")
            )
