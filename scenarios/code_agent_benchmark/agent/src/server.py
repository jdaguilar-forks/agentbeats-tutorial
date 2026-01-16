"""A2A server for code agent."""

import argparse

from a2a.server import Server

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

    executor = Executor(model=args.model)
    server = Server(executor=executor)

    print(f"Starting Code Agent on {args.host}:{args.port} with model {args.model}")
    server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
