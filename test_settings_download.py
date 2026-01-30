#!/usr/bin/env python3
"""Manual test for Settings window model download functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.settings_window import SettingsWindow

def test_settings_download():
    """Test the Settings window model download UI."""
    print("=" * 70)
    print("Manual Test: Settings Window - Model Download")
    print("=" * 70)
    print()
    print("This test will open the Settings window.")
    print()
    print("INSTRUCTIONS:")
    print("1. Click on the 'Local STT' tab")
    print("2. In the 'Download Model' section, enter a model ID (e.g., 'tiny')")
    print("3. Click the 'Download' button")
    print("4. You should see:")
    print("   - A confirmation dialog asking if you want to download")
    print("   - A 'Downloading' message while downloading")
    print("   - A 'Download Complete' message when finished")
    print("   - The model should appear in the 'Available Models' list")
    print("5. Test error handling by entering an invalid model ID (e.g., 'invalid')")
    print("   - You should see an error notification")
    print()
    print("Press Enter to start the test...")
    input()

    # Create config
    config = Config()

    # Create and show settings window
    settings = SettingsWindow(config)
    settings.show()

    print("\n✓ Test complete!")
    print("If the download worked correctly, the story passes.")

if __name__ == "__main__":
    test_settings_download()
