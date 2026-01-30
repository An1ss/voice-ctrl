"""Local audio transcription module using faster-whisper."""

import logging
from pathlib import Path
from .notifier import Notifier
from .config import Config


class LocalTranscriber:
    """Transcribes audio files using faster-whisper locally."""

    def __init__(self, config=None):
        """Initialize the local transcriber.

        Args:
            config: Config object (if None, will create a new one)
        """
        # Use provided config or create new one
        self.config = config if config else Config()

        # Set default paths
        config_dir = Path.home() / ".config" / "voice-ctrl"
        self.log_path = config_dir / "voice-ctrl.log"

        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self._setup_logging()

        # Initialize notifier
        self.notifier = Notifier(log_path=self.log_path)

        # Load local STT configuration
        self.engine = self.config.get_local_engine()
        self.model_path = self.config.get_local_model_path()
        self.model_id = self.config.get_local_model_id()

        # Initialize model (lazy loading)
        self.model = None

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

    def _load_model(self):
        """Load the faster-whisper model.

        Returns:
            True if model loaded successfully, False otherwise
        """
        if self.model is not None:
            return True

        try:
            # Import faster_whisper here to avoid dependency issues
            from faster_whisper import WhisperModel

            # Determine which model to use: model_path or model_id
            if self.model_path and self.model_path.strip():
                # Use local model path
                model_source = self.model_path
                print(f"Loading local model from: {model_source}")
            elif self.model_id and self.model_id.strip():
                # Use model ID (Hugging Face model name)
                model_source = self.model_id
                print(f"Loading model by ID: {model_source}")
            else:
                # No model specified, use default
                model_source = "base"
                print(f"No model specified, using default: {model_source}")

            # Load the model
            # device can be "cpu", "cuda", or "auto"
            # compute_type can be "int8", "float16", "float32"
            self.model = WhisperModel(
                model_source,
                device="cpu",  # Default to CPU for compatibility
                compute_type="int8"  # Efficient on CPU
            )

            print(f"Successfully loaded faster-whisper model: {model_source}")
            return True

        except ImportError as e:
            error_msg = "faster-whisper library not installed"
            self.logger.error(f"{error_msg}: {e}")
            self.notifier.notify_transcription_error("Local STT not available - faster-whisper not installed")
            return False

        except Exception as e:
            error_msg = f"Failed to load faster-whisper model: {e}"
            self.logger.error(error_msg)
            self.notifier.notify_transcription_error(f"Failed to load local model: {str(e)[:50]}")
            return False

    def transcribe(self, audio_file_path):
        """Transcribe audio file using faster-whisper.

        Args:
            audio_file_path: Path to audio file (WAV format)

        Returns:
            Transcribed text as string, or None if error occurred
        """
        audio_path = Path(audio_file_path)

        try:
            # Check if audio file exists
            if not audio_path.exists():
                error_msg = f"Audio file not found: {audio_file_path}"
                self.logger.error(error_msg)
                print(f"ERROR: {error_msg}")
                self.notifier.notify_transcription_error("Audio file not found")
                return None

            # Load model if not already loaded
            if not self._load_model():
                return None

            print(f"Transcribing audio file with faster-whisper: {audio_file_path}")

            # Transcribe the audio file
            # faster-whisper returns segments, we need to combine them
            segments, info = self.model.transcribe(
                str(audio_path),
                language="en",  # Default to English
                beam_size=5,  # Default beam size
                vad_filter=True,  # Enable voice activity detection
            )

            # Combine all segments into a single text
            transcribed_text = " ".join(segment.text for segment in segments).strip()

            if transcribed_text:
                print(f"Transcription successful: {transcribed_text[:100]}..." if len(transcribed_text) > 100 else f"Transcription successful: {transcribed_text}")
                return transcribed_text
            else:
                print("No speech detected in audio")
                self.notifier.notify_transcription_error("No speech detected")
                return None

        except Exception as e:
            error_msg = f"Error during local transcription: {e}"
            self.logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            self.notifier.notify_transcription_error(f"Local transcription failed: {str(e)[:50]}")
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
