"""Main orchestrator for the AI Code Agent Benchmark wizard."""

import os
import subprocess

from dotenv import load_dotenv

from .config import ConfigManager
from .models import ModelSelector
from .ui import WizardUI


class BenchmarkWizard:
    """Orchestrates the wizard flow from start to execution."""

    def __init__(self, root_dir: str):
        load_dotenv()
        self.config_manager = ConfigManager(root_dir)
        self.model_selector = ModelSelector()
        self.root_dir = root_dir

    def _ensure_provider_prefix(self, provider_id: str, model_id: str) -> str:
        """Ensure model ID has correct provider prefix if needed."""
        # 1 is OpenRouter
        if provider_id == "1" and not model_id.startswith("openrouter/"):
            return f"openrouter/{model_id}"
        return model_id

    def run(self):
        """Execute the full wizard workflow."""
        WizardUI.print_banner()

        config = self.config_manager.load_config()
        WizardUI.print_current_setup(config)

        if config and WizardUI.ask_confirm("Use these settings?"):
            gen_model = config.get("generator_model")
            eval_model = config.get("evaluator_model")
            source = config.get("source", "bigcodebench")
        else:
            # 1. Select Generator
            gen_prov_id = WizardUI.select_provider(
                "Configure Generator (Purple Agent)", self.model_selector.PROVIDERS
            )
            gen_models = self.model_selector.get_models_for_provider(gen_prov_id)
            gen_model = WizardUI.select_from_list(
                f"Select Model for Generator ({self.model_selector.PROVIDERS[gen_prov_id]['name']})",
                gen_models,
            )
            gen_model = self._ensure_provider_prefix(gen_prov_id, gen_model)

            # Check Key
            key_name = self.model_selector.check_api_key(gen_prov_id)
            if key_name:
                key_val = WizardUI.prompt_api_key(key_name)
                self.config_manager.update_dotenv(key_name, key_val)
                os.environ[key_name] = key_val

            # 2. Select Evaluator
            print(
                "\nTip: Use a strong model (e.g. GPT-4o) if relying on LLM-as-a-Judge features."
            )
            eval_prov_id = WizardUI.select_provider(
                "Configure Evaluator (Green Agent)", self.model_selector.PROVIDERS
            )
            eval_models = self.model_selector.get_models_for_provider(eval_prov_id)
            eval_model = WizardUI.select_from_list(
                f"Select Model for Evaluator ({self.model_selector.PROVIDERS[eval_prov_id]['name']})",
                eval_models,
            )
            eval_model = self._ensure_provider_prefix(eval_prov_id, eval_model)

            # Check Key
            key_name = self.model_selector.check_api_key(eval_prov_id)
            if key_name:
                key_val = WizardUI.prompt_api_key(key_name)
                self.config_manager.update_dotenv(key_name, key_val)
                os.environ[key_name] = key_val

            # 3. Select Task Source
            source = WizardUI.select_task_source()

            # Save
            new_config = {
                "generator_model": gen_model,
                "evaluator_model": eval_model,
                "source": source,
            }
            self.config_manager.save_config(new_config)
            print("✓ Settings saved to benchmark_config.json")

        # Update Scenario file
        print("\nUpdating configuration file...")
        self.config_manager.update_scenario_toml(gen_model, eval_model, source)
        print(f"✓ Configuration updated in {self.config_manager.scenario_path}")

        # Execute
        print("\nStarting benchmark...")
        cmd = f"uv run agentbeats-run {self.config_manager.scenario_path}"
        print(f"Running: {cmd}\n")

        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Benchmark execution failed: {e}")
        except KeyboardInterrupt:
            print("\n👋 Benchmark stopped by user.")
