#!/usr/bin/env python3
"""Test script to verify Settings window tabs implementation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.settings_window import SettingsWindow

def main():
    """Test the settings window with three tabs."""
    print("Opening Settings window to verify three tabs...")
    print("Expected tabs: General, Online, Local")
    print("\nGeneral tab should have:")
    print("  - STT Provider selector")
    print("  - Max Recording Duration")
    print("  - Audio Feedback checkbox")
    print("  - Keyboard Shortcut")
    print("  - Start at Login checkbox")
    print("\nOnline tab should have:")
    print("  - OpenAI API Key field")
    print("\nLocal tab should have:")
    print("  - Local Engine selector")
    print("  - Model selection UI")
    print("  - Scan buttons")
    print("  - Download section")
    print("\n" + "="*60)

    # Load config
    config = Config()

    # Create and show settings window
    settings = SettingsWindow(config)
    settings.show()

if __name__ == "__main__":
    main()
