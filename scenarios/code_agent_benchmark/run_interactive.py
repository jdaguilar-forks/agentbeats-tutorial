#!/usr/bin/env python3
"""
Interactive Configuration Wizard for AgentBeats Code Benchmark.
Supports:
- Model selection for Generator (Purple Agent) and Evaluator (Green Agent)
- Multiple providers (OpenAI, Anthropic, Gemini, OpenRouter)
- Persistent configuration (benchmark_config.json)
- Automatic environment verification
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
from typing import List, Dict, Optional
from pathlib import Path

# Color codes for terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

SCENARIO_FILE = "scenarios/code_agent_benchmark/scenario_bigcodebench.toml"
CONFIG_FILE = "benchmark_config.json"

PROVIDERS = {
    "openrouter": "OpenRouter (Access to 100+ models)",
    "openai": "OpenAI (GPT-4o, GPT-3.5)",
    "anthropic": "Anthropic (Claude 3.5 Sonnet)",
    "gemini": "Google Gemini (Gemini 1.5 Pro/Flash)",
}

# Static curated lists for direct providers (since fetching requires specific SDKs)
STATIC_MODELS = {
    "openai": [
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
    ],
    "anthropic": [
        {"id": "claude-3-5-sonnet-20240620", "name": "Claude 3.5 Sonnet"},
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
    ],
    "gemini": [
        {"id": "gemini/gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
        {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
    ],
}


class ConfigManager:
    """Manages loading and saving of benchmark configuration."""

    def __init__(self):
        self.config = self._load()

    def _load(self) -> Dict:
        """Load config from JSON file if exists."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save(self, generator_model: str, evaluator_model: str):
        """Save current selection to config file."""
        self.config = {
            "generator_model": generator_model,
            "evaluator_model": evaluator_model,
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
            print(f"{GREEN}✓ Settings saved to {CONFIG_FILE}{RESET}")
        except Exception as e:
            print(f"{YELLOW}Warning: Could not save config: {e}{RESET}")

    def get_defaults(self) -> tuple[Optional[str], Optional[str]]:
        """Return (generator_model, evaluator_model) from config."""
        return self.config.get("generator_model"), self.config.get("evaluator_model")


class ModelSelector:
    """Handles fetching and listing models from providers."""

    def get_openrouter_models(self) -> List[Dict]:
        """Fetch available models from OpenRouter API."""
        print(f"{CYAN}Fetching OpenRouter models...{RESET}")
        try:
            url = "https://openrouter.ai/api/v1/models"
            req = urllib.request.Request(url, headers={"User-Agent": "AgentBeats/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                raw_models = data.get("data", [])

                # Filter for free/cheap or popular
                # Prioritize free models for demo purposes
                models = []
                for m in raw_models:
                    model_id = m["id"]
                    # Ensure prefix
                    if not model_id.startswith("openrouter/"):
                        model_id = f"openrouter/{model_id}"

                    price = m.get("pricing", {})
                    is_free = (
                        price.get("prompt") == "0" and price.get("completion") == "0"
                    )

                    name = m["name"]
                    if is_free:
                        name = f"{name} (Free)"

                    models.append({"id": model_id, "name": name, "free": is_free})

                # Sort: Free first, then alphabetical
                models.sort(key=lambda x: (not x["free"], x["name"]))
                return models
        except Exception as e:
            print(f"{RED}Error fetching OpenRouter models: {e}{RESET}")
            return []

    def select_provider(self, role_name: str) -> str:
        """Interactive provider selection."""
        print(f"\n{BOLD}Select Provider for {role_name}:{RESET}")
        providers = list(PROVIDERS.keys())
        for i, key in enumerate(providers, 1):
            print(f"{i}. {PROVIDERS[key]}")

        while True:
            try:
                choice = input(f"{GREEN}Choose (1-{len(providers)}): {RESET}")
                idx = int(choice) - 1
                if 0 <= idx < len(providers):
                    return providers[idx]
            except ValueError:
                pass
            print(f"{RED}Invalid selection.{RESET}")

    def select_model(self, provider: str, role_name: str) -> str:
        """Interactive model selection based on provider."""
        print(f"\n{BOLD}Select Model for {role_name} ({PROVIDERS[provider]}):{RESET}")

        models = []
        if provider == "openrouter":
            models = self.get_openrouter_models()
            # If fetch failed, fallback
            if not models:
                models = [
                    {
                        "id": "openrouter/google/gemini-2.0-flash-exp:free",
                        "name": "Gemini 2.0 Flash Exp (Free)",
                    },
                    {
                        "id": "openrouter/meta-llama/llama-3-8b-instruct:free",
                        "name": "Llama 3 8B (Free)",
                    },
                    {"id": "openrouter/openai/gpt-4o-mini", "name": "GPT-4o Mini"},
                ]
        else:
            models = STATIC_MODELS.get(provider, [])

        # Display models
        # For OpenRouter, list is long, so we paginate or show top 20
        display_limit = 20
        if len(models) > display_limit:
            print(
                f"{YELLOW}(Showing top {display_limit} of {len(models)} models){RESET}"
            )

        for i, m in enumerate(models[:display_limit], 1):
            print(f"{i}. {m['name']} ({m['id']})")

        print(f"{YELLOW}0. Manual Log Entry (Type custom model ID){RESET}")

        while True:
            try:
                choice = input(
                    f"{GREEN}Choose (1-{min(len(models), display_limit)}) or 0 for manual: {RESET}"
                )
                if choice == "0":
                    return input(f"{GREEN}Enter model ID: {RESET}")

                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]["id"]
            except ValueError:
                pass
            print(f"{RED}Invalid selection.{RESET}")


class Wizard:
    """Orchestrates the configuration flow."""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.selector = ModelSelector()

    def check_env_keys(self, model_id: str):
        """Warn if API key might be missing for the selected model."""
        # Simple heuristic check
        needed_key = None
        if "openrouter" in model_id:
            needed_key = "OPEN_ROUTER_API_KEY"
        elif model_id.startswith("gpt"):
            needed_key = "OPENAI_API_KEY"
        elif "claude" in model_id:
            needed_key = "ANTHROPIC_API_KEY"
        elif "gemini" in model_id:
            needed_key = "GEMINI_API_KEY"

        if needed_key:
            # Check env var or .env file
            has_key = os.environ.get(needed_key) is not None
            if not has_key and os.path.exists(".env"):
                with open(".env", "r") as f:
                    if needed_key in f.read():
                        has_key = True

            if not has_key:
                print(f"{YELLOW}Warning: {needed_key} not found in environment.{RESET}")
                print(
                    f"Please enter your {needed_key} to proceed (or press Enter to skip):"
                )

                key_input = input(f"{GREEN}> {RESET}").strip()
                if key_input:
                    # Set in current env
                    os.environ[needed_key] = key_input

                    # Append to .env
                    try:
                        with open(".env", "a") as f:
                            # ensure newline prefix if file does not end with newline
                            # Read last char first? Simpler to just prepend newline if file exists and is not empty
                            f.write(f'\n{needed_key}="{key_input}"')
                        print(f"{GREEN}✓ Saved {needed_key} to .env{RESET}")
                    except Exception as e:
                        print(f"{RED}Failed to save to .env: {e}{RESET}")
                else:
                    print(f"{RED}Skipping key entry. Benchmark may fail.{RESET}")

    def update_scenario_file(self, gen_model: str, eval_model: str):
        """Update scenario_bigcodebench.toml with selected models."""
        print(f"\n{CYAN}Updating configuration file...{RESET}")

        try:
            with open(SCENARIO_FILE, "r") as f:
                content = f.read()

            # 1. Update Generator (Code Agent - Port 9019)
            # Regex: (port 9019.*?--model\s+)[^\s\"]+  OR insert if not present
            gen_pattern = r"(port 9019.*?)(--model\s+[^\s\"]+)?"

            def gen_replacement(match):
                prefix = match.group(1)
                # Ensure we don't duplicate flags if regex matched weirdly
                return f"{prefix}--model {gen_model}"

            # Simple replace if regex is too brittle for optional groups
            # Let's use a robust approach: Replace the whole cmd string based on port
            # Assuming standard structure: cmd = "python ... --port 9019 ..."

            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if "port 9020" in line and "cmd =" in line:
                    # Generator line
                    # Reconstruct command to ensure clean slate
                    base_cmd = "python scenarios/code_agent_benchmark/agent/src/server.py --host 127.0.0.1 --port 9020"
                    new_lines.append(f'cmd = "{base_cmd} --model {gen_model}"')
                elif "port 9010" in line and "cmd =" in line:
                    # Evaluator line
                    base_cmd = "python scenarios/code_agent_benchmark/evaluator/src/server.py --host 127.0.0.1 --port 9010"
                    new_lines.append(f'cmd = "{base_cmd} --model {eval_model}"')
                else:
                    new_lines.append(line)

            with open(SCENARIO_FILE, "w") as f:
                f.write("\n".join(new_lines))

            print(f"{GREEN}✓ Configuration updated in {SCENARIO_FILE}{RESET}")
            return True

        except Exception as e:
            print(f"{RED}Error updating scenario file: {e}{RESET}")
            return False

    def run(self):
        print(f"{CYAN}=========================================={RESET}")
        print(f"{CYAN}   AgentBeats Benchmark Wizard   {RESET}")
        print(f"{CYAN}=========================================={RESET}")

        # Load defaults
        def_gen, def_eval = self.config_manager.get_defaults()

        if def_gen and def_eval:
            print(f"\n{BOLD}Found Setup:{RESET}")
            print(f"Generator: {GREEN}{def_gen}{RESET}")
            print(f"Evaluator: {GREEN}{def_eval}{RESET}")

            choice = input(f"\n{YELLOW}Use these settings? [Y/n]: {RESET}").lower()
            if choice not in ("n", "no"):
                self.update_scenario_file(def_gen, def_eval)
                self.check_env_keys(def_gen)
                self.check_env_keys(def_eval)
                self.launch_benchmark()
                return

        # Configure Generator
        print(f"\n{CYAN}--- Configure Generator (Purple Agent) ---{RESET}")
        prov = self.selector.select_provider("Generator")
        gen_model = self.selector.select_model(prov, "Generator")

        # Configure Evaluator
        print(f"\n{CYAN}--- Configure Evaluator (Green Agent) ---{RESET}")
        print(
            f"{YELLOW}Tip: Use a strong model (e.g. GPT-4o) if relying on LLM-as-a-Judge features.{RESET}"
        )
        prov = self.selector.select_provider("Evaluator")
        eval_model = self.selector.select_model(prov, "Evaluator")

        # Save and Update
        self.config_manager.save(gen_model, eval_model)
        if self.update_scenario_file(gen_model, eval_model):
            self.check_env_keys(gen_model)
            self.check_env_keys(eval_model)
            self.launch_benchmark()

    def launch_benchmark(self):
        print(f"\n{GREEN}Starting benchmark...{RESET}")
        print(f"{CYAN}Running: uv run agentbeats-run {SCENARIO_FILE}{RESET}\n")
        try:
            subprocess.run(["uv", "run", "agentbeats-run", SCENARIO_FILE], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n{RED}Benchmark run failed with exit code {e.returncode}{RESET}")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Benchmark cancelled by user.{RESET}")


if __name__ == "__main__":
    Wizard().run()
