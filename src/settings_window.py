"""Settings window module for VoiceControl application."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
from pathlib import Path
import threading
import os
import subprocess
from .model_scanner import ModelScanner


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
        self.model_scanner = ModelScanner(log_path=config.log_path)
        self.discovered_models = []  # List of discovered models

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
        self.window.geometry("700x650")
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

        # Start at Login
        row += 1
        ttk.Label(main_frame, text="Start at Login:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        autostart_var = tk.BooleanVar(value=self.config.is_autostart_enabled())
        autostart_check = ttk.Checkbutton(
            main_frame,
            text="Start VoiceControl automatically when I log in",
            variable=autostart_var
        )
        autostart_check.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['autostart_enabled'] = autostart_var

        # Separator
        row += 1
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 15))

        # Local Model Discovery section
        row += 1
        model_section_label = ttk.Label(
            main_frame,
            text="Local Model Discovery",
            font=("", 12, "bold")
        )
        model_section_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Model scanning buttons
        row += 1
        scan_button_frame = ttk.Frame(main_frame)
        scan_button_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=8)

        scan_default_button = ttk.Button(
            scan_button_frame,
            text="Scan Default Paths",
            command=self._scan_default_paths,
            width=18
        )
        scan_default_button.grid(row=0, column=0, padx=(0, 10))

        scan_folder_button = ttk.Button(
            scan_button_frame,
            text="Scan Folder...",
            command=self._scan_custom_folder,
            width=18
        )
        scan_folder_button.grid(row=0, column=1)

        # Discovered models list
        row += 1
        ttk.Label(main_frame, text="Detected Models:").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5)
        )

        # Scrollable text widget for model list
        row += 1
        models_frame = ttk.Frame(main_frame)
        models_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.models_text = scrolledtext.ScrolledText(
            models_frame,
            height=6,
            width=70,
            state='disabled',
            wrap=tk.WORD
        )
        self.models_text.pack(fill=tk.BOTH, expand=True)

        # Initially show placeholder text
        self._update_models_display([])

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

            # Handle autostart configuration
            autostart_enabled = self.entry_widgets['autostart_enabled'].get()
            old_autostart_enabled = self.config.is_autostart_enabled()
            current_config['autostart_enabled'] = autostart_enabled

            # Create or remove autostart file if setting changed
            if autostart_enabled != old_autostart_enabled:
                if autostart_enabled:
                    if not self._create_autostart_file():
                        messagebox.showwarning(
                            "Autostart Warning",
                            "Settings saved, but failed to create autostart file.\n"
                            "You may need to configure autostart manually."
                        )
                else:
                    if not self._remove_autostart_file():
                        messagebox.showwarning(
                            "Autostart Warning",
                            "Settings saved, but failed to remove autostart file.\n"
                            "You may need to remove it manually from ~/.config/autostart/"
                        )

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

    def _get_autostart_path(self):
        """Get the path to the autostart desktop file.

        Returns:
            Path object for ~/.config/autostart/voice-ctrl.desktop
        """
        return Path.home() / ".config" / "autostart" / "voice-ctrl.desktop"

    def _get_executable_path(self):
        """Get the path to the voice-ctrl executable.

        Returns:
            Path to voice-ctrl command (checks /usr/bin first, falls back to python -m)
        """
        # Check if installed via .deb package
        usr_bin_path = Path("/usr/bin/voice-ctrl")
        if usr_bin_path.exists():
            return str(usr_bin_path)

        # Fallback to running from source with absolute path
        project_root = Path(__file__).parent.parent
        return f"bash -c 'cd {project_root} && python3 -m src.main'"

    def _create_autostart_file(self):
        """Create the autostart desktop file."""
        try:
            autostart_path = self._get_autostart_path()
            executable = self._get_executable_path()

            # Ensure autostart directory exists
            autostart_path.parent.mkdir(parents=True, exist_ok=True)

            # Create desktop file content
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=VoiceControl
Comment=System-wide voice dictation tool
Exec={executable}
Icon=voice-ctrl
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
Categories=Utility;Accessibility;
"""

            # Write desktop file
            with open(autostart_path, 'w') as f:
                f.write(desktop_content)

            print(f"Autostart file created at: {autostart_path}")
            return True
        except Exception as e:
            print(f"Failed to create autostart file: {e}")
            return False

    def _remove_autostart_file(self):
        """Remove the autostart desktop file."""
        try:
            autostart_path = self._get_autostart_path()
            if autostart_path.exists():
                autostart_path.unlink()
                print(f"Autostart file removed: {autostart_path}")
            return True
        except Exception as e:
            print(f"Failed to remove autostart file: {e}")
            return False

    def _scan_default_paths(self):
        """Scan default paths for models in background thread."""
        # Show scanning message
        self._update_models_display([], scanning=True)

        # Start scan in background
        def on_scan_complete(models):
            # Update UI from main thread
            self.window.after(0, lambda: self._on_models_discovered(models))

        self.model_scanner.scan_default_paths(callback=on_scan_complete)

    def _scan_custom_folder(self):
        """Prompt user to select a folder and scan it."""
        folder = filedialog.askdirectory(title="Select folder to scan for models")
        if folder:
            # Show scanning message
            self._update_models_display([], scanning=True)

            # Scan synchronously (since user is waiting)
            def scan_worker():
                models = self.model_scanner.scan_folder_sync(folder)
                # Update UI from main thread
                self.window.after(0, lambda: self._on_models_discovered(models))

            # Run in background thread
            thread = threading.Thread(target=scan_worker, daemon=True)
            thread.start()

    def _on_models_discovered(self, models):
        """Handle discovered models.

        Args:
            models: List of model dictionaries with 'name' and 'path' keys
        """
        self.discovered_models = models
        self._update_models_display(models)

        if models:
            messagebox.showinfo(
                "Models Found",
                f"Found {len(models)} model(s).\n\n"
                "Models are listed below with their paths.\n"
                "You can copy the path to use in local_model_path config."
            )
        else:
            messagebox.showinfo(
                "No Models Found",
                "No Whisper models were detected in the scanned locations.\n\n"
                "Try scanning a different folder or download a model first."
            )

    def _update_models_display(self, models, scanning=False):
        """Update the models text widget with discovered models.

        Args:
            models: List of model dictionaries
            scanning: If True, show "Scanning..." message
        """
        self.models_text.config(state='normal')
        self.models_text.delete(1.0, tk.END)

        if scanning:
            self.models_text.insert(tk.END, "Scanning for models...\n")
            self.models_text.insert(tk.END, "This may take a moment.\n")
        elif not models:
            self.models_text.insert(tk.END, "No models found yet.\n")
            self.models_text.insert(tk.END, "Click 'Scan Default Paths' or 'Scan Folder...' to search for models.\n")
        else:
            for i, model in enumerate(models, 1):
                self.models_text.insert(tk.END, f"{i}. {model['name']}\n")
                self.models_text.insert(tk.END, f"   Path: {model['path']}\n\n")

        self.models_text.config(state='disabled')


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
