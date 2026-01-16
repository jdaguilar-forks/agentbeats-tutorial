"""Messenger utility for A2A communication with purple agents."""

import httpx
from a2a.types import Message
from a2a.utils import new_task, new_user_text_message


class Messenger:
    """A2A client for communicating with purple agents."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
        self.active_tasks: dict[str, str] = {}

    async def talk_to_agent(self, prompt: str, agent_url: str) -> str:
        """Send a message to an agent and get the response text."""
        message = new_user_text_message(prompt)
        task = new_task(message)

        response = await self.client.post(
            f"{agent_url}/tasks",
            json={
                "message": message.model_dump(mode="json"),
                "task": task.model_dump(mode="json"),
            },
        )
        response.raise_for_status()

        # Extract text from response
        response_data = response.json()
        if "parts" in response_data:
            for part in response_data["parts"]:
                if "text" in part:
                    return part["text"]

        return ""

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def reset(self):
        """Reset messenger state."""
        self.active_tasks.clear()
