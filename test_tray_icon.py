"""Test script for tray icon functionality."""

import time
from src.tray_icon import TrayIcon


def test_tray_icon():
    """Test tray icon creation and state changes."""
    print("Testing tray icon...")

    # Create tray icon
    tray_icon = TrayIcon(tooltip="Voice Control")
    print("✓ TrayIcon instance created")

    # Start tray icon
    tray_icon.start()
    print("✓ Tray icon started")
    print("  Check your system tray for a gray microphone icon")

    # Wait a bit
    time.sleep(2)

    # Test switching to recording state
    print("\nSwitching to recording state...")
    tray_icon.set_recording_state(True)
    print("✓ Icon should now be red")

    time.sleep(2)

    # Test switching back to idle state
    print("\nSwitching back to idle state...")
    tray_icon.set_recording_state(False)
    print("✓ Icon should now be gray")

    time.sleep(2)

    # Stop tray icon
    print("\nStopping tray icon...")
    tray_icon.stop()
    print("✓ Tray icon stopped")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    try:
        test_tray_icon()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
