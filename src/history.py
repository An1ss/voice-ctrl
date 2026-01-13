"""History management module for VoiceControl application."""

import json
from pathlib import Path
from datetime import datetime
import logging


class HistoryManager:
    """Manages transcription history storage and retrieval."""

    MAX_ENTRIES = 30  # Maximum number of entries to keep

    def __init__(self, history_path=None):
        """Initialize the history manager.

        Args:
            history_path: Path to history file (defaults to ~/.config/voice-ctrl/history.json)
        """
        config_dir = Path.home() / ".config" / "voice-ctrl"
        self.history_path = Path(history_path) if history_path else config_dir / "history.json"

        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Load existing history
        self.entries = self._load_history()

    def _load_history(self):
        """Load history from file.

        Returns:
            List of history entries (most recent first)
        """
        try:
            if not self.history_path.exists():
                # Create empty history file
                self._save_history([])
                return []

            with open(self.history_path, 'r') as f:
                data = json.load(f)

            # Validate data structure
            if not isinstance(data, list):
                self.logger.warning("Invalid history file format. Creating new history.")
                return []

            # Validate each entry has required fields
            valid_entries = []
            for entry in data:
                if self._validate_entry(entry):
                    valid_entries.append(entry)
                else:
                    self.logger.warning(f"Skipping invalid history entry: {entry}")

            return valid_entries

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse history file: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error loading history: {e}")
            return []

    def _save_history(self, entries):
        """Save history to file.

        Args:
            entries: List of history entries to save
        """
        try:
            with open(self.history_path, 'w') as f:
                json.dump(entries, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save history: {e}")

    def _validate_entry(self, entry):
        """Validate a history entry has required fields.

        Args:
            entry: Dictionary containing history entry

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(entry, dict):
            return False

        required_fields = ['timestamp', 'text', 'duration_seconds']
        for field in required_fields:
            if field not in entry:
                return False

        # Validate types
        if not isinstance(entry['timestamp'], str):
            return False
        if not isinstance(entry['text'], str):
            return False
        if not isinstance(entry['duration_seconds'], (int, float)):
            return False

        return True

    def add_entry(self, text, duration_seconds):
        """Add a new transcription to history.

        Args:
            text: Transcribed text
            duration_seconds: Duration of the audio in seconds
        """
        # Create new entry with current timestamp
        entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'text': text,
            'duration_seconds': duration_seconds
        }

        # Add to beginning of list (most recent first)
        self.entries.insert(0, entry)

        # Trim to maximum entries (keep most recent 30)
        if len(self.entries) > self.MAX_ENTRIES:
            self.entries = self.entries[:self.MAX_ENTRIES]

        # Save to file
        self._save_history(self.entries)

        self.logger.info(f"Added history entry: {text[:50]}... (duration: {duration_seconds}s)")

    def get_entries(self):
        """Get all history entries.

        Returns:
            List of history entries (most recent first)
        """
        return self.entries.copy()

    def clear_history(self):
        """Clear all history entries."""
        self.entries = []
        self._save_history(self.entries)
        self.logger.info("History cleared")

    def get_entry_count(self):
        """Get the number of history entries.

        Returns:
            Number of entries
        """
        return len(self.entries)
