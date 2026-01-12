#!/usr/bin/env python3
"""Test script for notification functionality."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.notifier import Notifier


def main():
    """Test various notification types."""
    print("Testing notification system...")
    print("You should see desktop notifications appear on your screen.\n")

    notifier = Notifier()

    # Test 1: No audio detected
    print("Test 1: No audio detected notification")
    notifier.notify_no_audio()
    time.sleep(2)

    # Test 2: API failure
    print("Test 2: API failure notification")
    notifier.notify_api_failure("Service unavailable")
    time.sleep(2)

    # Test 3: Network timeout
    print("Test 3: Network timeout notification")
    notifier.notify_network_timeout()
    time.sleep(2)

    # Test 4: Invalid API key
    print("Test 4: Invalid API key notification")
    notifier.notify_invalid_api_key()
    time.sleep(2)

    # Test 5: Transcription error
    print("Test 5: Transcription error notification")
    notifier.notify_transcription_error("Audio format not supported")
    time.sleep(2)

    print("\nAll tests completed!")
    print(f"Check log file at: {notifier.log_path}")

    # Display log contents
    if notifier.log_path.exists():
        print("\nLog file contents:")
        print("-" * 60)
        with open(notifier.log_path, 'r') as f:
            print(f.read())
        print("-" * 60)
    else:
        print(f"\nWarning: Log file not found at {notifier.log_path}")


if __name__ == "__main__":
    main()
