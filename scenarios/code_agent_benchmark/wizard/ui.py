"""UI and CLI utilities for the AI Code Agent Benchmark wizard."""

import os
from typing import Dict, List, Any


class WizardUI:
    """Handles console interactions and output formatting."""

    @staticmethod
    def print_banner():
        """Print the wizard welcome banner."""
        os.system("clear" if os.name == "posix" else "cls")
        print("==========================================")
        print("   AgentBeats Benchmark Wizard   ")
        print("==========================================")
        print()

    @staticmethod
    def print_current_setup(config: Dict[str, Any]):
        """Print the currently loaded benchmark configuration."""
        if config:
            print("Found Setup:")
            print(f"Generator: {config.get('generator_model')}")
            print(f"Evaluator: {config.get('evaluator_model')}")
            print(f"Task Source: {config.get('source', 'bigcodebench')}")
            print()

    @staticmethod
    def ask_confirm(message: str, default: str = "y") -> bool:
        """Ask user for a yes/no confirmation."""
        choice = input(
            f"{message} [{default.upper()}/{'n' if default == 'y' else 'y'}]: "
        ).lower()
        if not choice:
            choice = default
        return choice == "y"

    @staticmethod
    def select_from_list(
        title: str,
        items: List[Dict[str, str]],
        id_key: str = "id",
        name_key: str = "name",
    ) -> str:
        """Present a list of items and ask the user to select one."""
        print(f"--- {title} ---")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item[name_key]}")
        print("0. Manual Entry (Type custom ID)")

        while True:
            choice = input(f"Choose (1-{len(items)}) or 0 for manual: ")
            if choice == "0":
                return input("Enter custom ID: ")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    return items[idx][id_key]
            except ValueError:
                pass
            print(f"Invalid choice. Please enter 0-{len(items)}.")

    @staticmethod
    def select_provider(title: str, providers: Dict[str, Dict[str, str]]) -> str:
        """Present provider options and ask user to select one."""
        print(f"--- {title} ---")
        sorted_keys = sorted(providers.keys())
        for k in sorted_keys:
            print(f"{k}. {providers[k]['name']}")

        while True:
            choice = input(f"Choose ({min(sorted_keys)}-{max(sorted_keys)}): ")
            if choice in providers:
                return choice
            print("Invalid choice.")

    @staticmethod
    def select_task_source() -> str:
        """Ask user to select the task source (BigCodeBench or Local)."""
        print("--- Select Task Source ---")
        print("1. BigCodeBench (300+ standard library tasks)")
        print("2. Local (scenarios/code_agent_benchmark/tasks/code_generation)")

        while True:
            choice = input("Choose (1-2): ")
            if choice == "1":
                return "bigcodebench"
            if choice == "2":
                return "local"
            print("Invalid choice.")

    @staticmethod
    def prompt_api_key(key_name: str) -> str:
        """Prompt user for a missing API key with basic validation."""
        while True:
            print(f"\n⚠️  Missing API Key: {key_name}")
            val = input(f"Enter your {key_name}: ").strip()
            if len(val) > 10:  # Most API keys are reasonably long
                return val
            print("❌ Invalid key format. Please enter a valid API key.")
