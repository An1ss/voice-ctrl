"""Settings window module for VoiceControl application."""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
import threading


class SettingsWindow:
    """Manages the settings GUI window."""

    def __init__(self, config, recorder=None):
        """Initialize the settings window.

        Args:
            config: Config instance containing current settings
            recorder: AudioRecorder instance for test recording (optional)
        """
        self.config = config
        self.recorder = recorder
        self.window = None
        self.entry_widgets = {}

    def show(self):
        """Show the settings window."""
        if self.window is not None:
            # Window already exists, bring it to front
            self.window.lift()
            self.window.focus_force()
            return

        # Create new window
        self.window = tk.Tk()
        self.window.title("Voice Control Settings")
        self.window.geometry("600x420")
        self.window.resizable(False, False)

        # Configure window grid to center the content
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        # Create main frame with padding (content will be centered)
        main_frame = ttk.Frame(self.window, padding="25")
        main_frame.grid(row=0, column=0)

        # Configure column weights for proper expansion of entry fields
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Voice Control Settings",
            font=("", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # API Key
        row = 1
        ttk.Label(main_frame, text="OpenAI API Key:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        api_key_entry = ttk.Entry(main_frame, show="*")
        api_key_entry.insert(0, self.config.get_api_key())
        api_key_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8, padx=(15, 0))
        self.entry_widgets['api_key'] = api_key_entry

        # Max Duration
        row += 1
        ttk.Label(main_frame, text="Max Recording Duration (seconds):").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        duration_entry = ttk.Entry(main_frame)
        duration_entry.insert(0, str(self.config.get_max_duration()))
        duration_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8, padx=(15, 0))
        self.entry_widgets['max_duration_seconds'] = duration_entry

        # Audio Feedback
        row += 1
        ttk.Label(main_frame, text="Audio Feedback (beeps):").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        audio_feedback_var = tk.BooleanVar(value=self.config.is_audio_feedback_enabled())
        audio_feedback_check = ttk.Checkbutton(
            main_frame,
            text="Enable beeps on start/stop",
            variable=audio_feedback_var
        )
        audio_feedback_check.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['audio_feedback_enabled'] = audio_feedback_var

        # Keyboard Shortcut
        row += 1
        ttk.Label(main_frame, text="Keyboard Shortcut:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        shortcut_entry = ttk.Entry(main_frame)
        shortcut_entry.insert(0, self.config.get_keyboard_shortcut())
        shortcut_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8, padx=(15, 0))
        self.entry_widgets['keyboard_shortcut'] = shortcut_entry

        # Note about restart
        row += 1
        note_label = ttk.Label(
            main_frame,
            text="Note: Changes to keyboard shortcut require app restart",
            font=("", 9, "italic"),
            foreground="gray"
        )
        note_label.grid(row=row, column=0, columnspan=2, pady=(10, 20))

        # Buttons frame
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(15, 0))

        # Test Recording button
        test_button = ttk.Button(
            button_frame,
            text="Test Recording",
            command=self._test_recording,
            width=15
        )
        test_button.grid(row=0, column=0, padx=8)

        # Save button
        save_button = ttk.Button(
            button_frame,
            text="Save",
            command=self._save_settings,
            width=12
        )
        save_button.grid(row=0, column=1, padx=8)

        # Cancel button
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._close_window,
            width=12
        )
        cancel_button.grid(row=0, column=2, padx=8)

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        # Run the window
        self.window.mainloop()

    def _test_recording(self):
        """Test recording functionality."""
        if self.recorder is None:
            messagebox.showinfo(
                "Test Recording",
                "Test recording is not available.\n\n"
                "Please use the keyboard shortcut to test recording."
            )
            return

        # Check if already recording
        if self.recorder.is_recording:
            messagebox.showwarning(
                "Test Recording",
                "Recording is already in progress.\n\n"
                "Press the keyboard shortcut to stop it first."
            )
            return

        # Show instructions
        result = messagebox.showinfo(
            "Test Recording",
            "Test recording will start when you click OK.\n\n"
            "Speak for a few seconds, then use your keyboard shortcut to stop.\n\n"
            "The transcribed text will be pasted automatically."
        )

        # Start recording
        if result:
            # Toggle recording (start)
            self.recorder.toggle_recording()
            messagebox.showinfo(
                "Recording Started",
                "Recording started!\n\n"
                "Use your keyboard shortcut to stop when done speaking."
            )

    def _save_settings(self):
        """Save settings to config file."""
        try:
            # Read current config file
            config_path = self.config.config_path
            if config_path.exists():
                with open(config_path, 'r') as f:
                    current_config = json.load(f)
            else:
                current_config = {}

            # Update with new values
            current_config['api_key'] = self.entry_widgets['api_key'].get()

            # Validate and convert max_duration_seconds
            try:
                max_duration = int(self.entry_widgets['max_duration_seconds'].get())
                if max_duration <= 0:
                    messagebox.showerror(
                        "Invalid Value",
                        "Max recording duration must be a positive number."
                    )
                    return
                current_config['max_duration_seconds'] = max_duration
            except ValueError:
                messagebox.showerror(
                    "Invalid Value",
                    "Max recording duration must be a valid number."
                )
                return

            current_config['audio_feedback_enabled'] = self.entry_widgets['audio_feedback_enabled'].get()
            current_config['keyboard_shortcut'] = self.entry_widgets['keyboard_shortcut'].get()

            # Save to file
            with open(config_path, 'w') as f:
                json.dump(current_config, f, indent=2)

            # Update config object in memory
            self.config.settings = current_config

            messagebox.showinfo(
                "Settings Saved",
                "Settings have been saved successfully!\n\n"
                "Note: Some changes (like keyboard shortcut) require restarting the application."
            )

            self._close_window()

        except Exception as e:
            messagebox.showerror(
                "Save Failed",
                f"Failed to save settings:\n{str(e)}"
            )

    def _close_window(self):
        """Close the settings window."""
        if self.window:
            self.window.destroy()
            self.window = None


def show_about_dialog():
    """Show the About dialog."""
    about_window = tk.Tk()
    about_window.title("About Voice Control")
    about_window.geometry("500x320")
    about_window.resizable(False, False)

    # Main frame with more padding
    frame = ttk.Frame(about_window, padding="40")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Configure frame to center content
    about_window.columnconfigure(0, weight=1)
    about_window.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    # Title
    title_label = ttk.Label(
        frame,
        text="Voice Control",
        font=("", 18, "bold"),
        justify=tk.CENTER
    )
    title_label.grid(row=0, column=0, pady=(0, 10))

    # Version
    version_label = ttk.Label(
        frame,
        text="Version 1.0.0",
        font=("", 11),
        justify=tk.CENTER
    )
    version_label.grid(row=1, column=0, pady=(0, 25))

    # Description
    desc_label = ttk.Label(
        frame,
        text="System-wide voice dictation tool for Ubuntu\n"
             "using OpenAI Whisper API\n\n"
             "Record audio with a keyboard shortcut,\n"
             "transcribe using AI, and paste automatically.",
        justify=tk.CENTER,
        font=("", 10)
    )
    desc_label.grid(row=2, column=0, pady=(0, 30))

    # Close button
    close_button = ttk.Button(
        frame,
        text="Close",
        command=about_window.destroy,
        width=15
    )
    close_button.grid(row=3, column=0)

    about_window.mainloop()
