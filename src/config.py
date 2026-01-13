"""Configuration management module for VoiceControl."""

import json
import logging
from pathlib import Path
from .notifier import Notifier


class Config:
    """Manages application configuration loading and validation."""

    # Default configuration values
    DEFAULT_CONFIG = {
        "api_key": "",
        "max_duration_seconds": 240,
        "audio_feedback_enabled": True
    }

    def __init__(self, config_path=None, log_path=None):
        """Initialize the configuration manager.

        Args:
            config_path: Path to config file (defaults to ~/.config/voice-ctrl/config.json)
            log_path: Path to log file (defaults to ~/.config/voice-ctrl/voice-ctrl.log)
        """
        # Set default paths
        config_dir = Path.home() / ".config" / "voice-ctrl"
        self.config_path = Path(config_path) if config_path else config_dir / "config.json"
        self.log_path = Path(log_path) if log_path else config_dir / "voice-ctrl.log"

        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self._setup_logging()

        # Initialize notifier
        self.notifier = Notifier(log_path=self.log_path)

        # Load configuration
        self.settings = self._load_config()

    def _setup_logging(self):
        """Configure logging to file."""
        logging.basicConfig(
            filename=str(self.log_path),
            level=logging.ERROR,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            force=True
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self):
        """Load configuration from file or create default config.

        Returns:
            Dictionary containing configuration settings
        """
        try:
            # If config file doesn't exist, create it with defaults
            if not self.config_path.exists():
                print(f"Config file not found. Creating default config at: {self.config_path}")
                self._create_default_config()
                return self.DEFAULT_CONFIG.copy()

            # Load existing config
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            # Validate config structure
            if not self._validate_config(config):
                error_msg = "Invalid config file structure"
                self.logger.error(error_msg)
                self.notifier.notify_error(
                    "Configuration Error",
                    f"Invalid config file. Using defaults. Check {self.log_path}"
                )
                return self.DEFAULT_CONFIG.copy()

            # Merge with defaults to ensure all keys exist
            merged_config = self.DEFAULT_CONFIG.copy()

            # Handle backward compatibility: openai_api_key -> api_key
            if "openai_api_key" in config and not config.get("api_key"):
                config["api_key"] = config["openai_api_key"]

            merged_config.update(config)

            print(f"Configuration loaded from: {self.config_path}")
            return merged_config

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in config file: {e}"
            self.logger.error(error_msg)
            self.notifier.notify_error(
                "Configuration Error",
                f"Invalid JSON in config file. Using defaults. Error: {str(e)[:50]}"
            )
            return self.DEFAULT_CONFIG.copy()

        except Exception as e:
            error_msg = f"Error loading config file: {e}"
            self.logger.error(error_msg)
            self.notifier.notify_error(
                "Configuration Error",
                f"Failed to load config. Using defaults. Check {self.log_path}"
            )
            return self.DEFAULT_CONFIG.copy()

    def _create_default_config(self):
        """Create a default configuration file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2)
            print(f"Default config file created at: {self.config_path}")
            print("Please edit the config file to add your OpenAI API key.")
        except Exception as e:
            error_msg = f"Failed to create default config file: {e}"
            self.logger.error(error_msg)
            print(f"ERROR: {error_msg}")

    def _validate_config(self, config):
        """Validate configuration structure and types.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(config, dict):
            return False

        # Check that api_key is a string
        if "api_key" in config and not isinstance(config["api_key"], str):
            return False

        # Check that max_duration_seconds is a positive number
        if "max_duration_seconds" in config:
            if not isinstance(config["max_duration_seconds"], (int, float)):
                return False
            if config["max_duration_seconds"] <= 0:
                return False

        # Check that audio_feedback_enabled is a boolean
        if "audio_feedback_enabled" in config and not isinstance(config["audio_feedback_enabled"], bool):
            return False

        return True

    def get(self, key, default=None):
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.settings.get(key, default)

    def get_api_key(self):
        """Get the OpenAI API key from config.

        Returns:
            API key string or empty string if not set
        """
        return self.settings.get("api_key", "")

    def get_max_duration(self):
        """Get the maximum recording duration in seconds.

        Returns:
            Maximum duration in seconds (default 240)
        """
        return self.settings.get("max_duration_seconds", 240)

    def is_audio_feedback_enabled(self):
        """Check if audio feedback (beeps) is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.settings.get("audio_feedback_enabled", True)
