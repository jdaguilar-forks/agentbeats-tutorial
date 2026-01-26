"""Configuration management for the AI Code Agent Benchmark wizard."""

import json
import os
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = "benchmark_config.json"
SCENARIO_FILE = "scenarios/code_agent_benchmark/scenario_bigcodebench.toml"


class ConfigManager:
    """Manages persistent configuration and environment settings."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.config_path = self.root_dir / CONFIG_FILE
        self.scenario_path = self.root_dir / SCENARIO_FILE

    def load_config(self) -> Dict[str, Any]:
        """Load benchmark configuration from JSON file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save benchmark configuration to JSON file."""
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

    def update_dotenv(self, key: str, value: str) -> None:
        """Update or add a key-value pair in the .env file."""
        dotenv_path = self.root_dir / ".env"
        current_content = ""
        if dotenv_path.exists():
            with open(dotenv_path, "r") as f:
                current_content = f.read()

        lines = current_content.splitlines()
        key_found = False
        new_lines = []

        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}")
                key_found = True
            else:
                new_lines.append(line)

        if not key_found:
            new_lines.append(f"{key}={value}")

        with open(dotenv_path, "w") as f:
            f.write("\n".join(new_lines) + "\n")

    def update_scenario_toml(
        self, gen_model: str, eval_model: str, source: str
    ) -> None:
        """Update the scenario TOML file with selected models and source."""
        if not self.scenario_path.exists():
            return

        with open(self.scenario_path, "r") as f:
            content = f.read()

        lines = content.split("\n")
        new_lines = []
        for line in lines:
            # Update Generator line (Port 9020)
            if "port 9020" in line and "cmd =" in line:
                base_cmd = "python scenarios/code_agent_benchmark/agent/src/server.py --host 127.0.0.1 --port 9020"
                new_lines.append(f'cmd = "{base_cmd} --model {gen_model}"')
            # Update Evaluator line (Port 9010)
            elif "port 9010" in line and "cmd =" in line:
                base_cmd = "python scenarios/code_agent_benchmark/evaluator/src/server.py --host 127.0.0.1 --port 9010"
                new_lines.append(f'cmd = "{base_cmd} --model {eval_model}"')
            # Update source line
            elif line.startswith("source ="):
                new_lines.append(f'source = "{source}"')
            else:
                new_lines.append(line)

        with open(self.scenario_path, "w") as f:
            f.write("\n".join(new_lines))
