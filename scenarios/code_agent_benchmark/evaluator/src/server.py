"""A2A server for code benchmark evaluator."""

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
    parser = argparse.ArgumentParser(
        description="Code Benchmark Evaluator (Green Agent)"
    )
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9009, help="Port to listen on")
    parser.add_argument("--card-url", type=str, help="Agent card URL")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="LLM model to use for evaluation (optional)",
    )
    args = parser.parse_args()

    skill = AgentSkill(
        id="run_code_benchmark",
        name="Evaluates code agents",
        description="Runs a benchmark to evaluate code agents on coding tasks.",
        tags=["code", "benchmark"],
        examples=[
            """
{
  "participants": {
    "code_agent": "http://127.0.0.1:9019"
  },
  "config": {
    "category": "code_generation",
    "num_tasks": 5
  }
}
""".strip()
        ],
    )

    agent_card = AgentCard(
        name="Code Benchmark Evaluator",
        description="Evaluates agents on code generation tasks.",
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

    print(f"Starting Code Benchmark Evaluator on {args.host}:{args.port}")
    uvicorn.run(server.build(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
