"""A2A server for code benchmark evaluator."""

import argparse

from a2a.server import Server

from executor import Executor


def main():
    parser = argparse.ArgumentParser(
        description="Code Benchmark Evaluator (Green Agent)"
    )
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9009, help="Port to listen on")
    parser.add_argument("--card-url", type=str, help="Agent card URL")
    args = parser.parse_args()

    executor = Executor()
    server = Server(executor=executor)

    print(f"Starting Code Benchmark Evaluator on {args.host}:{args.port}")
    server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
