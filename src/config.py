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
        "audio_feedback_enabled": True,
        "keyboard_shortcut": "Ctrl+Shift+Space",
        "autostart_enabled": False,
        "stt_provider": "openai",  # "openai" or "local"
        "local_engine": "faster-whisper",  # Local STT engine to use
        "local_model_path": "",  # Path to local model file
        "local_model_id": "",  # Hugging Face model ID (e.g., "openai/whisper-small")
        "local_scan_paths": []  # List of paths to scan for models
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

            # Check if migration is needed (config is missing some default keys)
            needs_migration = False
            for key in self.DEFAULT_CONFIG:
                if key not in config:
                    needs_migration = True
                    break

            # If migration is needed, write the complete config back to disk
            if needs_migration:
                print(f"Migrating config file to include missing parameters...")
                try:
                    with open(self.config_path, 'w') as f:
                        json.dump(merged_config, f, indent=2)
                    print(f"Config migration complete. All parameters initialized.")
                except Exception as e:
                    error_msg = f"Failed to migrate config file: {e}"
                    self.logger.error(error_msg)
                    print(f"WARNING: {error_msg}")

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

        # Check that keyboard_shortcut is a string
        if "keyboard_shortcut" in config and not isinstance(config["keyboard_shortcut"], str):
            return False

        # Check that autostart_enabled is a boolean
        if "autostart_enabled" in config and not isinstance(config["autostart_enabled"], bool):
            return False

        # Check that stt_provider is a valid string value
        if "stt_provider" in config:
            if not isinstance(config["stt_provider"], str):
                return False
            if config["stt_provider"] not in ["openai", "local"]:
                self.logger.error(f"Invalid stt_provider value: {config['stt_provider']}. Must be 'openai' or 'local'")
                self.notifier.notify_error(
                    "Configuration Error",
                    f"Invalid stt_provider: '{config['stt_provider']}'. Using default 'openai'."
                )
                config["stt_provider"] = "openai"  # Revert to default

        # Check that local_engine is a string
        if "local_engine" in config and not isinstance(config["local_engine"], str):
            return False

        # Check that local_model_path is a string
        if "local_model_path" in config and not isinstance(config["local_model_path"], str):
            return False

        # Check that local_model_id is a string
        if "local_model_id" in config and not isinstance(config["local_model_id"], str):
            return False

        # Check that local_scan_paths is a list
        if "local_scan_paths" in config:
            if not isinstance(config["local_scan_paths"], list):
                return False
            # Ensure all items in the list are strings
            if not all(isinstance(path, str) for path in config["local_scan_paths"]):
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

    def get_keyboard_shortcut(self):
        """Get the keyboard shortcut from config.

        Returns:
            Keyboard shortcut string (default "Ctrl+Shift+Space")
        """
        return self.settings.get("keyboard_shortcut", "Ctrl+Shift+Space")

    def is_autostart_enabled(self):
        """Check if autostart is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.settings.get("autostart_enabled", False)

    def get_stt_provider(self):
        """Get the STT provider to use.

        Returns:
            STT provider string: "openai" or "local" (default "openai")
        """
        return self.settings.get("stt_provider", "openai")

    def get_local_engine(self):
        """Get the local STT engine to use.

        Returns:
            Local engine string (default "faster-whisper")
        """
        return self.settings.get("local_engine", "faster-whisper")

    def get_local_model_path(self):
        """Get the path to the local model file.

        Returns:
            Model path string or empty string if not set
        """
        return self.settings.get("local_model_path", "")

    def get_local_model_id(self):
        """Get the Hugging Face model ID for local models.

        Returns:
            Model ID string or empty string if not set
        """
        return self.settings.get("local_model_id", "")

    def get_local_scan_paths(self):
        """Get the list of paths to scan for local models.

        Returns:
            List of path strings (default empty list)
        """
        return self.settings.get("local_scan_paths", [])
