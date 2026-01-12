"""Audio transcription module using OpenAI Whisper API."""

import json
import logging
import os
from pathlib import Path
from openai import OpenAI
from openai import APIError, APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from .notifier import Notifier


class WhisperTranscriber:
    """Transcribes audio files using OpenAI Whisper API."""

    def __init__(self, config_path=None, log_path=None):
        """Initialize the Whisper transcriber.

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

        # Load API key from config
        self.api_key = self._load_api_key()

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key, timeout=30.0) if self.api_key else None

    def _setup_logging(self):
        """Configure logging to file."""
        logging.basicConfig(
            filename=str(self.log_path),
            level=logging.ERROR,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def _load_api_key(self):
        """Load OpenAI API key from config file.

        Returns:
            API key string, or None if not found or error occurred
        """
        try:
            if not self.config_path.exists():
                error_msg = f"Config file not found: {self.config_path}"
                self.logger.error(error_msg)
                print(f"ERROR: {error_msg}")
                # Note: notifier not initialized yet at this point
                return None

            with open(self.config_path, 'r') as f:
                config = json.load(f)

            api_key = config.get('openai_api_key')
            if not api_key:
                error_msg = "OpenAI API key not found in config file"
                self.logger.error(error_msg)
                print(f"ERROR: {error_msg}")
                # Note: notifier not initialized yet at this point
                return None

            return api_key

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in config file: {e}"
            self.logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            # Note: notifier not initialized yet at this point
            return None
        except Exception as e:
            error_msg = f"Error loading config file: {e}"
            self.logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            # Note: notifier not initialized yet at this point
            return None

    def transcribe(self, audio_file_path):
        """Transcribe audio file using OpenAI Whisper API.

        Args:
            audio_file_path: Path to audio file (WAV format)

        Returns:
            Transcribed text as string, or None if error occurred
        """
        audio_path = Path(audio_file_path)

        try:
            # Check if client is initialized (API key loaded)
            if not self.client:
                self.notifier.notify_invalid_api_key()
                return None

            # Check if audio file exists
            if not audio_path.exists():
                error_msg = f"Audio file not found: {audio_file_path}"
                self.logger.error(error_msg)
                print(f"ERROR: {error_msg}")
                self.notifier.notify_transcription_error("Audio file not found")
                return None

            print(f"Transcribing audio file: {audio_file_path}")

            # Open and send audio file to Whisper API
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Default to English, can be auto-detected
                )

            # Extract transcribed text
            transcribed_text = transcript.text
            print(f"Transcription successful: {transcribed_text[:100]}..." if len(transcribed_text) > 100 else f"Transcription successful: {transcribed_text}")

            return transcribed_text

        except AuthenticationError as e:
            self.notifier.notify_invalid_api_key()
            return None

        except APITimeoutError as e:
            self.notifier.notify_network_timeout()
            return None

        except RateLimitError as e:
            self.notifier.notify_api_failure("Rate limit exceeded")
            return None

        except APIConnectionError as e:
            self.notifier.notify_api_failure("Network connection error")
            return None

        except APIError as e:
            self.notifier.notify_api_failure(str(e))
            return None

        except Exception as e:
            error_msg = f"Unexpected error during transcription: {e}"
            self.notifier.notify_transcription_error(error_msg)
            return None

        finally:
            # Clean up temporary audio file
            self._cleanup_audio_file(audio_path)

    def _cleanup_audio_file(self, audio_path):
        """Delete temporary audio file after transcription.

        Args:
            audio_path: Path object to audio file
        """
        try:
            if audio_path.exists():
                audio_path.unlink()
                print(f"Cleaned up temporary audio file: {audio_path}")
        except Exception as e:
            error_msg = f"Error deleting temporary audio file {audio_path}: {e}"
            self.logger.error(error_msg)
            print(f"WARNING: {error_msg}")
