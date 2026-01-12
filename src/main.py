"""Main entry point for VoiceControl application."""

from pynput import keyboard
from recorder import AudioRecorder


def main():
    """Main function to run the voice control application."""
    print("VoiceControl started!")
    print("Press Ctrl+Shift+Space to start/stop recording")
    print("Press Ctrl+C to exit\n")

    # Initialize audio recorder
    recorder = AudioRecorder()

    def on_hotkey():
        """Callback function when hotkey is pressed."""
        recorder.toggle_recording()

    # Set up global hotkey listener
    # Using GlobalHotKeys for cross-platform global hotkey support
    hotkey = keyboard.GlobalHotKeys({
        '<ctrl>+<shift>+<space>': on_hotkey
    })

    hotkey.start()

    try:
        # Keep the application running
        hotkey.join()
    except KeyboardInterrupt:
        print("\nExiting VoiceControl...")
        # Stop recording if still active
        if recorder.is_recording:
            recorder.stop_recording()
        hotkey.stop()


if __name__ == "__main__":
    main()
