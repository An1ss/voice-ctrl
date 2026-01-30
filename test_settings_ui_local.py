#!/usr/bin/env python3
"""Test script for Settings window with Local STT tab."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.settings_window import SettingsWindow

def main():
    """Test the settings window."""
    print("Testing Settings Window with Local STT tab...")

    # Create config
    config = Config()

    # Create and show settings window
    print("Opening settings window...")
    print("\nTest the following:")
    print("1. General tab shows all existing settings")
    print("2. Local STT tab appears")
    print("3. STT provider selector has openai/local options")
    print("4. Local engine selector shows faster-whisper")
    print("5. Model selection UI is visible")
    print("6. Scan buttons work")
    print("7. Model list is selectable")
    print("8. Copy button copies model path")
    print("9. Download model field and button are visible")
    print("10. Save button saves all settings")

    settings = SettingsWindow(config)
    settings.show()

if __name__ == "__main__":
    main()
