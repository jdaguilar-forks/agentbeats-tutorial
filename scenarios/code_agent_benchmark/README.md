# Code Agent Benchmark

This benchmark evaluates AI agents on code generation tasks using realistic programming challenges.

## Overview

The **Code Agent Benchmark** tests AI agents' ability to generate correct Python code from natural language specifications. It includes:

- **5 sample tasks** adapted from HumanEval covering various programming concepts
- **Automated evaluation** using pytest for correctness
- **Scoring system** based on test pass rates and code quality
- **A2A protocol** integration for standardized agent communication

## Architecture

- **Green Agent (Evaluator)**: Orchestrates the benchmark, sends tasks to agents, runs tests, and computes scores
- **Purple Agent (Baseline)**: Simple LLM-based agent that solves coding tasks (serves as a baseline for comparison)

## Setup

1. **Install dependencies**:
   ```bash
   cd scenarios/code_agent_benchmark
   pip install -r requirements.txt
   ```
   
   Or using uv from the project root:
   ```bash
   uv sync
   ```

2. **Set up API keys** (for the baseline agent):
   ```bash
   cp ../../sample.env ../../.env
   # Edit .env and add your OPENAI_API_KEY or other LLM provider key
   ```

## Running the Benchmark

From the project root:

```bash
uv run agentbeats-run scenarios/code_agent_benchmark/scenario.toml
```

This will:
1. Start the evaluator (green agent) on port 9009
2. Start the baseline agent (purple agent) on port 9019
3. Run the benchmark with 5 code generation tasks
4. Display results with pass/fail status and scores

### Options

Edit `scenario.toml` to configure:

```toml
[config]
category = "code_generation"
num_tasks = 5           # Number of tasks to run
# difficulty = "easy"   # Optional: filter by difficulty
```

You can also modify the purple agent model:

```toml
[participants]]
cmd = "python scenarios/code_agent_benchmark/agent/src/server.py --host 127.0.0.1 --port 9019 --model gpt-4o"
```

## Task Format

Tasks are defined in JSON format in `tasks/code_generation/`. Each task includes:

- **Function specification**: Name, parameters, return type
- **Description**: Natural language explanation
- **Test cases**: pytest-compatible tests
- **Reference solution**: For validation

Example task structure:

```json
{
  "id": "code_gen_001",
  "category": "code_generation",
  "difficulty": "easy",
  "title": "Check if List Has Close Elements",
  "prompt": "...",
  "test_code": "...",
  "reference_solution": "..."
}
```

## Evaluation Criteria

Each submission is scored based on:

- **Test Pass Rate (50%)**: Percentage of test cases passed
- **Correctness (30%)**: All tests pass bonus
- **Code Quality (20%)**: Basic quality checks

Final scores range from 0.0 to 1.0.

## Adding Custom Tasks

1. Create a new JSON file in `tasks/code_generation/`
2. Follow the task format (see existing files)
3. Ensure test cases are comprehensive
4. Update `num_tasks` in `scenario.toml` if needed

## Docker Deployment

Build and run with Docker:

```bash
# Build images
docker build --platform linux/amd64 -f Dockerfile.evaluator -t code-benchmark-evaluator .
docker build --platform linux/amd64 -f Dockerfile.agent -t code-benchmark-agent .

# Run evaluator
docker run -p 9009:9009 code-benchmark-evaluator --host 0.0.0.0 --port 9009

# Run agent (in another terminal)
docker run -p 9019:9019 -e OPENAI_API_KEY=your-key code-benchmark-agent --host 0.0.0.0 --port 9019
```

## Extending the Benchmark

### Adding More Categories

1. Create a new directory in `tasks/` (e.g., `bug_fixing/`)
2. Add task JSON files
3. Create a new evaluator in `evaluator/src/evaluators/` (e.g., `bug_fix_evaluator.py`)
4. Register it in `evaluator/src/agent.py`

### Testing Your Own Agent

Replace the baseline agent with your own implementation:

1. Implement an A2A-compatible agent that:
   - Receives task descriptions via A2A messages
   - Returns Python code as a text message
2. Update `scenario.toml` to point to your agent endpoint
3. Run the benchmark

## Results

Benchmark results include:

- **Task-level scores**: Individual pass/fail for each task
- **Aggregate metrics**: Total pass rate, average score
- **Detailed output**: Test failures, error messages
- **A2A artifacts**: Structured JSON results for analysis

## Troubleshooting

**Port already in use**: Update ports in `scenario.toml`

**Tests failing**: Check that submissions include all necessary imports and match the expected function signature

**Agent timeouts**: Increase timeout in `evaluator/src/utils/test_runner.py`

## License

This benchmark is part of the AgentBeats tutorial and follows the same license.
