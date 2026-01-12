"""Main entry point for VoiceControl application."""

from pynput import keyboard
from .recorder import AudioRecorder
from .transcriber import WhisperTranscriber
from .paster import TextPaster
from .tray_icon import TrayIcon


def main():
    """Main function to run the voice control application."""
    print("VoiceControl started!")
    print("Press Ctrl+Shift+Space to start/stop recording")
    print("Press Ctrl+C to exit\n")

    # Initialize components
    recorder = AudioRecorder()
    transcriber = WhisperTranscriber()
    paster = TextPaster(restore_clipboard=True)
    tray_icon = TrayIcon()

    # Start system tray icon
    tray_icon.start()

    def on_hotkey():
        """Callback function when hotkey is pressed."""
        audio_file = recorder.toggle_recording()

        # Update tray icon based on recording state
        tray_icon.set_recording_state(recorder.is_recording)

        # If recording just stopped, transcribe and paste
        if audio_file:
            print("Processing audio...")
            transcribed_text = transcriber.transcribe(audio_file)

            if transcribed_text:
                print("Pasting transcribed text...")
                paster.paste_text(transcribed_text)
            else:
                print("No transcription result to paste")

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
        # Stop tray icon
        tray_icon.stop()
        hotkey.stop()


if __name__ == "__main__":
    main()
