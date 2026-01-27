# AI Code Agent Benchmark

A comprehensive, multi-source evaluation suite for testing AI agents on realistic Python coding tasks.

## 🌟 Key Features

- **Interactive Wizard**: Effortlessly configure providers (OpenAI, Anthropic, Gemini, OpenRouter) and models via a guided CLI.
- **BigCodeBench Integration**: Support for the industry-standard `bigcodebench` dataset (standard-library-only subset).
- **Flexible Task Sources**: Toggle between standard BigCodeBench tasks and local custom JSON tasks.
- **Modular Architecture**: Separate responsibilities for UI, configuration, orchestration, and reporting.
- **A2A Protocol**: Fully standardized inter-agent communication using JSON-RPC 2.0.

## 🚀 Getting Started

### 1. Installation
Ensure you have `uv` installed, then sync the environment:
```bash
uv sync
```

### 2. Launch the Wizard
The simplest way to run a benchmark is using the interactive wizard:
```bash
uv run python scenarios/code_agent_benchmark/run_interactive.py
```
The wizard will:
- Let you choose providers and models for both the **Generator** and **Evaluator**.
- Check for missing API keys and help you save them to `.env`.
- Allow you to select the task source (**BigCodeBench** or **Local**).
- Automatically update configurations and launch the benchmark.

## 📂 Project Structure

- **`wizard/`**: Modular package handling the interactive CLI and configuration logic.
- **`agent/`**: The "Purple Agent" source — a baseline LLM-driven code generator.
- **`evaluator/`**: The "Green Agent" source — orchestrates the benchmark and evaluates submissions.
- **`tasks/`**: Directory for local custom benchmark tasks in JSON format.
- **`scenario_bigcodebench.toml`**: The main configuration file used by `agentbeats-run`.

## 🛠️ Advanced Usage

### Manual Execution
If you prefer not to use the wizard, you can edit `scenario_bigcodebench.toml` directly and run:
```bash
uv run agentbeats-run scenarios/code_agent_benchmark/scenario_bigcodebench.toml
```

### Debugging & Artifacts
Execution logs and generated code snippets are stored in the gitignored `debug/` folder for easy inspection. Successful runs produce a **"Benchmark Results"** artifact with detailed pass/fail metrics and test outputs.

## 📂 Task Sources

1. **BigCodeBench**: 300+ standard-library-only tasks. Ideal for broad model evaluation.
2. **Local**: Custom tasks located in `scenarios/code_agent_benchmark/tasks/code_generation`. Best for specialized testing.

## 📜 License

This benchmark is part of the AgentBeats tutorial and follows the same license terms.
