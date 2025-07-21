import yaml
import os
from typing import Dict, Any, Optional
import logging


class Config:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()

    def _load_config(self):
        """Load and parse YAML configuration file"""
        try:
            with open(self.config_path, "r") as file:
                self.config = yaml.safe_load(file)

            if self.config is None:
                self.config = {}

            self._replace_env_vars()
            self.logger.info(
                f"Successfully loaded configuration from {self.config_path}"
            )

        except FileNotFoundError:
            self.logger.error(f"Configuration file {self.config_path} not found")
            self.config = {}
        except yaml.YAMLError as e:
            self.logger.error(f"YAML parsing error: {e}")
            self.config = {}
        except Exception as e:
            self.logger.error(f"Unexpected error loading config: {e}")
            self.config = {}

    def _replace_env_vars(self):
        """Recursively replace environment variable placeholders in configuration"""

        def replace_in_value(value):
            if isinstance(value, str):
                # Handle ${ENV_VAR} format
                if value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    return os.getenv(
                        env_var, value
                    )  # Return original if env var not found
                # Handle $ENV_VAR format
                elif value.startswith("$"):
                    env_var = value[1:]
                    return os.getenv(env_var, value)
            elif isinstance(value, dict):
                return {k: replace_in_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_in_value(item) for item in value]

            return value

        self.config = replace_in_value(self.config)

    def get(self, key: str, default=None) -> Any:
        """Get configuration value by key with optional default"""
        keys = key.split(".")
        current = self.config

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def get_site_config(self, site_name: str) -> Dict:
        """Get configuration for a specific site"""
        return self.get("test_sites", {}).get(site_name, {})

    def get_email_config(self) -> Dict:
        """Get email configuration section"""
        return self.get("email_config", {})

    def get_ai_config(self) -> Dict:
        """Get AI configuration section"""
        return self.get("ai_config", {})

    def get_timeout(self, timeout_type: str = "default") -> int:
        """Get timeout value in milliseconds"""
        timeouts = self.get("timeouts", {})
        return timeouts.get(timeout_type, timeouts.get("default", 30000))

    def get_polling_config(self) -> Dict:
        """Get email polling configuration"""
        return self.get("email_config.polling", {})

    def get_regex_patterns(self) -> Dict:
        """Get regex patterns for code extraction"""
        return self.get("regex_patterns", {})

    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        keys = key.split(".")
        current = self.config

        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the final value
        current[keys[-1]] = value

    def save_config(self, output_path: Optional[str] = None):
        """Save current configuration to file"""
        if output_path is None:
            output_path = self.config_path

        try:
            with open(output_path, "w") as file:
                yaml.safe_dump(
                    self.config,
                    file,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    indent=2,
                )
            self.logger.info(f"Configuration saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()

    def validate_required_keys(self, required_keys: list) -> bool:
        """Validate that required configuration keys exist"""
        missing_keys = []

        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)

        if missing_keys:
            self.logger.error(f"Missing required configuration keys: {missing_keys}")
            return False

        return True

    def load_multiple_configs(self, config_paths: list):
        """Load and merge multiple YAML configuration files"""
        merged_config = {}

        for path in config_paths:
            try:
                with open(path, "r") as file:
                    config_data = yaml.safe_load(file)
                    if config_data:
                        merged_config = self._deep_merge(merged_config, config_data)
                        self.logger.info(f"Merged configuration from {path}")
            except Exception as e:
                self.logger.warning(f"Failed to load config from {path}: {e}")

        self.config = merged_config
        self._replace_env_vars()

    def _deep_merge(self, dict1: dict, dict2: dict) -> dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()

        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_all_sites(self) -> Dict[str, Dict]:
        """Get all configured sites"""
        return self.get("test_sites", {})

    def add_site_config(self, site_name: str, site_config: Dict):
        """Add or update configuration for a site"""
        if "test_sites" not in self.config:
            self.config["test_sites"] = {}

        self.config["test_sites"][site_name] = site_config
        self.logger.info(f"Added/updated configuration for site: {site_name}")

    def is_ai_enabled(self) -> bool:
        """Check if AI functionality is enabled and properly configured"""
        ai_config = self.get_ai_config()
        return ai_config.get("enabled", False) and bool(ai_config.get("openai_api_key"))

    def __str__(self) -> str:
        """String representation of configuration (without sensitive data)"""
        safe_config = self._sanitize_for_display(self.config.copy())
        return yaml.safe_dump(safe_config, default_flow_style=False)

    def _sanitize_for_display(self, config: Any) -> Any:
        """Remove sensitive information from config for display"""
        if isinstance(config, dict):
            sanitized = {}
            for key, value in config.items():
                if any(
                    sensitive in key.lower()
                    for sensitive in ["password", "key", "secret", "token"]
                ):
                    sanitized[key] = "***HIDDEN***"
                else:
                    sanitized[key] = self._sanitize_for_display(value)
            return sanitized
        elif isinstance(config, list):
            return [self._sanitize_for_display(item) for item in config]
        else:
            return config


# Convenience function for quick config loading
def load_config(config_path: str = "config/config.yaml") -> Config:
    """Load configuration from YAML file"""
    return Config(config_path)
