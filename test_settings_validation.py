#!/usr/bin/env python3
"""Validation test for Settings window structure."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.settings_window import SettingsWindow

def main():
    """Validate settings window can be created."""
    print("Testing Settings Window creation...")

    # Create config
    config = Config()

    # Create settings window (don't show it)
    settings = SettingsWindow(config)

    # Validate structure
    assert settings.config is not None, "Config should be set"
    assert settings.entry_widgets is not None, "Entry widgets dict should exist"
    assert settings.model_scanner is not None, "Model scanner should exist"
    assert settings.discovered_models == [], "Discovered models should start empty"

    print("✓ SettingsWindow structure validated")
    print("✓ All dependencies initialized correctly")
    print("\nSettings window is ready for use!")
    print("\nTo manually test the UI:")
    print("  1. Run: python3 -m src.main")
    print("  2. Right-click tray icon")
    print("  3. Click 'Settings'")
    print("  4. Check both 'General' and 'Local STT' tabs")

if __name__ == "__main__":
    main()
