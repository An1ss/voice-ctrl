"""Desktop notification module using plyer library."""

import logging
from pathlib import Path
from plyer import notification


class Notifier:
    """Handles desktop notifications and error logging."""

    def __init__(self, log_path=None):
        """Initialize the notifier.

        Args:
            log_path: Path to log file (defaults to ~/.config/voice-ctrl/voice-ctrl.log)
        """
        # Set default log path
        config_dir = Path.home() / ".config" / "voice-ctrl"
        self.log_path = Path(log_path) if log_path else config_dir / "voice-ctrl.log"

        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging to file."""
        logging.basicConfig(
            filename=str(self.log_path),
            level=logging.ERROR,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            force=True  # Override any existing logging config
        )
        self.logger = logging.getLogger(__name__)

    def notify_error(self, error_type, message):
        """Show desktop notification and log error.

        Args:
            error_type: Type of error (e.g., "API Error", "Network Error")
            message: User-friendly error message
        """
        # Show desktop notification
        try:
            notification.notify(
                title=f"Voice Control - {error_type}",
                message=message,
                timeout=5  # 5 seconds for errors
            )
        except Exception as e:
            # If notification fails, just log it
            print(f"Failed to show notification: {e}")

        # Log the error
        self.logger.error(f"{error_type}: {message}")
        print(f"ERROR [{error_type}]: {message}")

    def notify_no_audio(self):
        """Notify user that no audio was detected."""
        self.notify_error(
            "No Audio Detected",
            "No audio was recorded. Please check your microphone and try again."
        )

    def notify_api_failure(self, details=""):
        """Notify user of API failure.

        Args:
            details: Optional details about the failure
        """
        message = "Failed to transcribe audio. Please try again."
        if details:
            message = f"{message} ({details})"
        self.notify_error("API Failure", message)

    def notify_network_timeout(self):
        """Notify user of network timeout."""
        self.notify_error(
            "Network Timeout",
            "Request timed out after 30 seconds. Please check your internet connection."
        )

    def notify_invalid_api_key(self):
        """Notify user of invalid API key."""
        self.notify_error(
            "Invalid API Key",
            "Your OpenAI API key is invalid. Please check your configuration file."
        )

    def notify_transcription_error(self, error_message):
        """Notify user of general transcription error.

        Args:
            error_message: Specific error message
        """
        self.notify_error(
            "Transcription Error",
            f"Unable to transcribe audio: {error_message}"
        )
