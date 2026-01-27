"""A2A server for code agent."""

import argparse

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from executor import Executor


def main():
    parser = argparse.ArgumentParser(description="Code Agent (Purple Agent)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9019, help="Port to listen on")
    parser.add_argument("--card-url", type=str, help="Agent card URL")
    parser.add_argument(
        "--model", type=str, default="gpt-4o-mini", help="LLM model to use"
    )
    args = parser.parse_args()

    skill = AgentSkill(
        id="solve_coding_tasks",
        name="Solve coding tasks",
        description="Solves a given coding task by generating Python code.",
        tags=["code", "solver"],
        examples=[
            """
Task: Check Palindrome
Description: Write a function that checks if a given string is a palindrome.

def is_palindrome(text: str) -> bool:
    ''' Checks if given string is a palindrome '''
    pass

Important: Return ONLY the complete Python code.
""".strip()
        ],
    )

    agent_card = AgentCard(
        name="Code Agent",
        description="Solves coding tasks using an LLM.",
        url=args.card_url or f"http://{args.host}:{args.port}/",
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=Executor(model=args.model),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    print(f"Starting Code Agent on {args.host}:{args.port} with model {args.model}")
    uvicorn.run(server.build(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
