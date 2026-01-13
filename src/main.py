"""Main entry point for VoiceControl application."""

import sys
from pynput import keyboard
from .config import Config
from .recorder import AudioRecorder
from .transcriber import WhisperTranscriber
from .paster import TextPaster
from .tray_icon import TrayIcon
from .settings_window import SettingsWindow, show_about_dialog
from .setup_wizard import SetupWizard, should_show_setup_wizard
from pathlib import Path


def parse_keyboard_shortcut(shortcut_str):
    """Parse a keyboard shortcut string into pynput format.

    Args:
        shortcut_str: String like "Ctrl+Shift+Space" or "Alt+F1"

    Returns:
        String in pynput format like "<ctrl>+<shift>+<space>" or None if invalid

    Examples:
        "Ctrl+Shift+Space" -> "<ctrl>+<shift>+<space>"
        "Alt+F1" -> "<alt>+<f1>"
        "Ctrl+A" -> "<ctrl>+a"
    """
    if not shortcut_str or not isinstance(shortcut_str, str):
        return None

    # Map of common key names to pynput format
    key_map = {
        "ctrl": "<ctrl>",
        "shift": "<shift>",
        "alt": "<alt>",
        "cmd": "<cmd>",
        "space": "<space>",
        "enter": "<enter>",
        "tab": "<tab>",
        "backspace": "<backspace>",
        "delete": "<delete>",
        "esc": "<esc>",
        "up": "<up>",
        "down": "<down>",
        "left": "<left>",
        "right": "<right>",
        "home": "<home>",
        "end": "<end>",
        "page_up": "<page_up>",
        "page_down": "<page_down>",
        "insert": "<insert>",
    }

    # Add function keys F1-F12
    for i in range(1, 13):
        key_map[f"f{i}"] = f"<f{i}>"

    try:
        # Split the shortcut by + and process each part
        parts = shortcut_str.split("+")
        if len(parts) < 2:
            return None  # Need at least modifier + key

        parsed_parts = []
        for part in parts:
            part_lower = part.strip().lower()

            # Check if it's a known modifier/special key
            if part_lower in key_map:
                parsed_parts.append(key_map[part_lower])
            # Single character keys (a-z, 0-9, etc.) stay lowercase
            elif len(part.strip()) == 1:
                parsed_parts.append(part.strip().lower())
            else:
                # Unknown key format
                return None

        return "+".join(parsed_parts)

    except Exception:
        return None


def main():
    """Main function to run the voice control application."""
    print("VoiceControl started!")

    # Load configuration
    config = Config()

    # Check if we need to show the setup wizard
    if should_show_setup_wizard(config):
        print("\nFirst time setup required...")
        config_path = Path.home() / ".config" / "voice-ctrl" / "config.json"
        wizard = SetupWizard(config_path)
        api_key = wizard.show()

        if api_key:
            # Reload config after setup
            config = Config()
            print("Setup complete! Starting VoiceControl...")
        else:
            print("Setup skipped. You can configure the API key later from Settings.")
            print("Note: Voice Control will not work without a valid API key.")

    # Get keyboard shortcut from config
    shortcut_str = config.get_keyboard_shortcut()
    parsed_shortcut = parse_keyboard_shortcut(shortcut_str)

    # Validate keyboard shortcut
    if not parsed_shortcut:
        error_msg = (
            f"Invalid keyboard shortcut: '{shortcut_str}'\n"
            "Valid format examples:\n"
            "  - Ctrl+Shift+Space\n"
            "  - Alt+F1\n"
            "  - Ctrl+Alt+R\n"
            "  - Shift+Insert\n"
            "\nPlease edit the config file at ~/.config/voice-ctrl/config.json\n"
            "and restart the application."
        )
        print(f"ERROR: {error_msg}")
        config.notifier.notify_error(
            "Invalid Keyboard Shortcut",
            f"'{shortcut_str}' is not valid. See console for examples."
        )
        sys.exit(1)

    print(f"Keyboard shortcut: {shortcut_str}")
    print("Press Ctrl+C to exit\n")

    # Initialize components with config settings
    recorder = AudioRecorder(
        max_duration=config.get_max_duration(),
        audio_feedback_enabled=config.is_audio_feedback_enabled()
    )
    transcriber = WhisperTranscriber(config=config)
    paster = TextPaster(restore_clipboard=True)

    # Define callback functions for tray menu
    def on_settings():
        """Show settings window."""
        settings_window = SettingsWindow(config, recorder)
        settings_window.show()

    def on_about():
        """Show about dialog."""
        show_about_dialog()

    def on_quit():
        """Quit the application."""
        print("\nQuitting VoiceControl...")
        if recorder.is_recording:
            recorder.stop_recording()
        sys.exit(0)

    # Initialize tray icon with menu callbacks
    tray_icon = TrayIcon(
        on_settings=on_settings,
        on_about=on_about,
        on_quit=on_quit
    )

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

    # Set up global hotkey listener with parsed shortcut
    # Using GlobalHotKeys for cross-platform global hotkey support
    try:
        hotkey = keyboard.GlobalHotKeys({
            parsed_shortcut: on_hotkey
        })
        hotkey.start()
    except Exception as e:
        error_msg = f"Failed to register keyboard shortcut '{shortcut_str}': {e}"
        print(f"ERROR: {error_msg}")
        config.notifier.notify_error(
            "Shortcut Registration Failed",
            f"Could not register '{shortcut_str}'. Try a different shortcut."
        )
        tray_icon.stop()
        sys.exit(1)

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
