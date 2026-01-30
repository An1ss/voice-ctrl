#!/usr/bin/env python3
"""Test script for settings window with model scanning."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.settings_window import SettingsWindow

def test_settings():
    """Test the settings window with model scanning."""
    print("Opening Settings window...")
    print("Test the model scanning buttons:")
    print("1. Click 'Scan Default Paths' to scan ~/.cache, ~/.local/share, ~/Downloads")
    print("2. Click 'Scan Folder...' to select a custom folder")
    print("3. Verify detected models are displayed with name and path")
    print()

    config = Config()
    settings = SettingsWindow(config)
    settings.show()

if __name__ == "__main__":
    test_settings()
