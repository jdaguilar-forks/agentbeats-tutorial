"""Messenger utility for A2A communication with purple agents."""

import httpx
from a2a.utils import new_task, new_agent_text_message


class Messenger:
    """A2A client for communicating with purple agents."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
        self.active_tasks: dict[str, str] = {}

    async def talk_to_agent(self, prompt: str, agent_url: str) -> str:
        """Send a message to an agent and get the response text (file path)."""
        message = new_agent_text_message(prompt)
        task = new_task(message)

        # Wrap in JSON-RPC 2.0
        payload = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": message.model_dump(mode="json"),
            },
            "id": "1",
        }

        response = await self.client.post(
            f"{agent_url.rstrip('/')}/",
            json=payload,
        )
        response.raise_for_status()

        # Extract text from response (could be code or file path)
        response_data = response.json()
        result = response_data.get("result")
        if not result:
            return ""

        # Result can be a Message or a Task according to A2A spec
        # Handle Task (standard for many A2A scenarios)
        if "status" in result and result["status"].get("message"):
            result = result["status"]["message"]

        # Handle Message (or Task's status message)
        if "parts" in result:
            for part in result["parts"]:
                if "text" in part:
                    return part["text"]

        return ""

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def reset(self):
        """Reset messenger state."""
        self.active_tasks.clear()
