# AI Code Agent Benchmark

A robust, multi-source evaluation suite for testing AI coding agents on realistic Python tasks. This benchmark supports both industry-standard datasets and local custom task suites, all within a standardized inter-agent communication framework.

---

## ⚡ Quickstart

Get up and running in less than 2 minutes.

### 1. Installation
Ensure you have `uv` installed, then synchronize the environment:
```bash
uv sync
```

### 2. Configure API Keys (Optional but Recommended)
Create a `.env` file in the project root with your provider keys:
```bash
# Example .env content
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
```

### 3. Launch the Interactive Wizard
Run the guided configuration tool to select your models and task source:
```bash
uv run python scenarios/code_agent_benchmark/run_interactive.py
```
The wizard will handle setting up the `scenario_bigcodebench.toml` and launching the benchmark for you.

---

## 🌟 Key Features

- **Interactive Wizard**: A guided CLI to configure providers (OpenAI, OpenRouter, etc.), models, and task sources without editing TOML files manually.
- **BigCodeBench Integration**: Built-in support for the `BigCodeBench` (StdLib) dataset, offering 300+ high-quality Python coding tasks.
- **Modular Architecture**: Clean separation of responsibilities between the **UI**, **Configuration**, **Orchestration** (Green Agent), and **Generation** (Purple Agent).
- **Extensible Task Sources**: Easily switch between standard benchmarks and your own custom JSON tasks in `tasks/code_generation`.
- **A2A Protocol**: Standardized inter-agent communication using JSON-RPC 2.0.

---

## 📂 Project Structure

- **`wizard/`**: The core logic for the interactive configuration and launch sequence.
- **`agent/`**: The "Purple Agent" — a reference LLM-driven code generation agent.
- **`evaluator/`**: The "Green Agent" — handles task loading, execution orchestration, and results reporting.
- **`tasks/`**: Custom local benchmark tasks.
- **`scenario_bigcodebench.toml`**: The main configuration file for `agentbeats-run`.

---

## 🛠️ Advanced Usage

### Manual Benchmark Execution
If you prefer direct control, you can edit the `scenario_bigcodebench.toml` and run:
```bash
uv run agentbeats-run scenarios/code_agent_benchmark/scenario_bigcodebench.toml
```

### Viewing Results & Debugging
- **Artifacts**: Every run generates a "Benchmark Results" artifact containing detailed pass/fail metrics.
- **Debug Logs**: Check the gitignored `debug/` folder for raw agent responses and execution logs.

---

## 📜 Task Sources

1. **BigCodeBench (StdLib)**: Focuses on complex Python logic using only the standard library. [Learn more](BIGCODEBENCH.md).
2. **Local Tasks**: HumanEval-style tasks stored locally for quick iteration and custom testing.

---

## 📜 License
This benchmark is part of the AgentBeats tutorial and follows the same license terms.
