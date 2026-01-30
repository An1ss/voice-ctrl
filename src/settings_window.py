"""Settings window module for VoiceControl application."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
from pathlib import Path
import threading
import os
import subprocess
import pyperclip
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
        self.selected_model_path = None  # Will be initialized when window is created

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
        self.window.geometry("800x700")
        self.window.resizable(False, False)

        # Initialize tk variables after window creation
        self.selected_model_path = tk.StringVar()

        # Configure window grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        # Create main frame with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Create tabs
        general_tab = ttk.Frame(notebook, padding="20")
        online_tab = ttk.Frame(notebook, padding="20")
        local_tab = ttk.Frame(notebook, padding="20")

        notebook.add(general_tab, text="General")
        notebook.add(online_tab, text="Online")
        notebook.add(local_tab, text="Local")

        # --- General Tab ---
        self._create_general_tab(general_tab)

        # --- Online Tab ---
        self._create_online_tab(online_tab)

        # --- Local STT Tab ---
        self._create_local_tab(local_tab)

        # Buttons frame (outside tabs, at bottom of window)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(10, 0))

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

    def _create_general_tab(self, parent):
        """Create the General settings tab.

        Args:
            parent: Parent frame for the tab content
        """
        # Configure column weights
        parent.columnconfigure(1, weight=1)

        row = 0

        # STT Provider
        ttk.Label(parent, text="STT Provider:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        provider_var = tk.StringVar(value=self.config.get_stt_provider())
        provider_combo = ttk.Combobox(
            parent,
            textvariable=provider_var,
            values=["openai", "local"],
            state="readonly",
            width=25
        )
        provider_combo.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['stt_provider'] = provider_var

        # Max Duration
        row += 1
        ttk.Label(parent, text="Max Recording Duration (seconds):").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        duration_entry = ttk.Entry(parent, width=20)
        duration_entry.insert(0, str(self.config.get_max_duration()))
        duration_entry.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['max_duration_seconds'] = duration_entry

        # Audio Feedback
        row += 1
        ttk.Label(parent, text="Audio Feedback (beeps):").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        audio_feedback_var = tk.BooleanVar(value=self.config.is_audio_feedback_enabled())
        audio_feedback_check = ttk.Checkbutton(
            parent,
            text="Enable beeps on start/stop",
            variable=audio_feedback_var
        )
        audio_feedback_check.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['audio_feedback_enabled'] = audio_feedback_var

        # Keyboard Shortcut
        row += 1
        ttk.Label(parent, text="Keyboard Shortcut:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        shortcut_entry = ttk.Entry(parent, width=30)
        shortcut_entry.insert(0, self.config.get_keyboard_shortcut())
        shortcut_entry.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['keyboard_shortcut'] = shortcut_entry

        # Start at Login
        row += 1
        ttk.Label(parent, text="Start at Login:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        autostart_var = tk.BooleanVar(value=self.config.is_autostart_enabled())
        autostart_check = ttk.Checkbutton(
            parent,
            text="Start VoiceControl automatically when I log in",
            variable=autostart_var
        )
        autostart_check.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['autostart_enabled'] = autostart_var

        # Note about restart
        row += 1
        note_label = ttk.Label(
            parent,
            text="Note: Changes to keyboard shortcut or STT provider require app restart",
            font=("", 9, "italic"),
            foreground="gray"
        )
        note_label.grid(row=row, column=0, columnspan=2, pady=(20, 0))

    def _create_online_tab(self, parent):
        """Create the Online STT settings tab.

        Args:
            parent: Parent frame for the tab content
        """
        # Configure column weights
        parent.columnconfigure(1, weight=1)

        row = 0

        # API Key
        ttk.Label(parent, text="OpenAI API Key:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        api_key_entry = ttk.Entry(parent, show="*", width=40)
        api_key_entry.insert(0, self.config.get_api_key())
        api_key_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8, padx=(15, 0))
        self.entry_widgets['api_key'] = api_key_entry

        # Help text
        row += 1
        help_text = ttk.Label(
            parent,
            text="Get your API key from https://platform.openai.com/api-keys",
            font=("", 9, "italic"),
            foreground="gray"
        )
        help_text.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

    def _create_local_tab(self, parent):
        """Create the Local STT settings tab.

        Args:
            parent: Parent frame for the tab content
        """
        # Configure column weights
        parent.columnconfigure(1, weight=1)

        row = 0

        # Local Engine
        ttk.Label(parent, text="Local Engine:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        engine_var = tk.StringVar(value=self.config.get_local_engine())
        engine_combo = ttk.Combobox(
            parent,
            textvariable=engine_var,
            values=["faster-whisper"],
            state="readonly",
            width=25
        )
        engine_combo.grid(row=row, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        self.entry_widgets['local_engine'] = engine_var

        # Model Selection Section
        row += 1
        ttk.Label(parent, text="Model Selection:", font=("", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(15, 5)
        )

        # Model Path (read-only, shows selected model)
        row += 1
        ttk.Label(parent, text="Selected Model Path:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        model_path_frame = ttk.Frame(parent)
        model_path_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8, padx=(15, 0))
        model_path_frame.columnconfigure(0, weight=1)

        # Use selected_model_path variable
        self.selected_model_path.set(self.config.get_local_model_path())
        model_path_entry = ttk.Entry(model_path_frame, textvariable=self.selected_model_path, state="readonly", width=50)
        model_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        copy_path_button = ttk.Button(
            model_path_frame,
            text="Copy",
            command=self._copy_model_path,
            width=8
        )
        copy_path_button.grid(row=0, column=1, padx=(5, 0))
        self.entry_widgets['local_model_path'] = self.selected_model_path

        # Discovered Models List
        row += 1
        ttk.Label(parent, text="Available Models:").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(15, 5)
        )

        # Model list with scrollbar and selection
        row += 1
        models_frame = ttk.Frame(parent)
        models_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        models_frame.columnconfigure(0, weight=1)

        # Create Listbox for model selection
        listbox_frame = ttk.Frame(models_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.models_listbox = tk.Listbox(
            listbox_frame,
            height=8,
            width=75,
            yscrollcommand=scrollbar.set
        )
        self.models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.models_listbox.yview)

        # Bind selection event
        self.models_listbox.bind('<<ListboxSelect>>', self._on_model_selected)

        # Model scanning buttons
        row += 1
        scan_button_frame = ttk.Frame(parent)
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
        scan_folder_button.grid(row=0, column=1, padx=(0, 10))

        refresh_button = ttk.Button(
            scan_button_frame,
            text="Refresh List",
            command=self._refresh_model_list,
            width=18
        )
        refresh_button.grid(row=0, column=2)

        # Model ID (for downloading)
        row += 1
        ttk.Label(parent, text="Download Model:", font=("", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(15, 5)
        )

        row += 1
        ttk.Label(parent, text="Model ID:").grid(
            row=row, column=0, sticky=tk.W, pady=8
        )
        model_id_frame = ttk.Frame(parent)
        model_id_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=8, padx=(15, 0))

        model_id_entry = ttk.Entry(model_id_frame, width=40)
        model_id_entry.insert(0, self.config.get_local_model_id())
        model_id_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.entry_widgets['local_model_id'] = model_id_entry

        download_button = ttk.Button(
            model_id_frame,
            text="Download",
            command=self._download_model,
            width=12
        )
        download_button.grid(row=0, column=1, padx=(10, 0))

        # Help text
        row += 1
        help_text = ttk.Label(
            parent,
            text="Examples: base, small, medium, large-v2, or openai/whisper-small",
            font=("", 9, "italic"),
            foreground="gray"
        )
        help_text.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=(0, 0), pady=(0, 5))

    def _copy_model_path(self):
        """Copy the selected model path to clipboard."""
        path = self.selected_model_path.get()
        if path:
            try:
                pyperclip.copy(path)
                messagebox.showinfo("Copied", "Model path copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Copy Failed", f"Failed to copy path: {str(e)}")
        else:
            messagebox.showwarning("No Path", "No model path selected")

    def _on_model_selected(self, event):
        """Handle model selection from listbox.

        Args:
            event: Listbox selection event
        """
        selection = self.models_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.discovered_models):
                model = self.discovered_models[index]
                self.selected_model_path.set(model['path'])

    def _refresh_model_list(self):
        """Refresh the model list, removing non-existent models."""
        # Filter out models whose paths no longer exist
        valid_models = []
        for model in self.discovered_models:
            path = Path(model['path'])
            if path.exists():
                valid_models.append(model)

        removed_count = len(self.discovered_models) - len(valid_models)
        self.discovered_models = valid_models
        self._update_models_list()

        if removed_count > 0:
            messagebox.showinfo(
                "List Refreshed",
                f"Removed {removed_count} model(s) that no longer exist.\n"
                f"{len(valid_models)} model(s) remaining."
            )
        else:
            messagebox.showinfo(
                "List Refreshed",
                f"All {len(valid_models)} model(s) are still valid."
            )

    def _download_model(self):
        """Download a model using the model ID."""
        model_id = self.entry_widgets['local_model_id'].get().strip()
        if not model_id:
            messagebox.showwarning(
                "No Model ID",
                "Please enter a model ID to download.\n\n"
                "Examples: base, small, medium, large-v2"
            )
            return

        # Show info dialog
        response = messagebox.askokcancel(
            "Download Model",
            f"This will download model: {model_id}\n\n"
            "The download may take several minutes depending on model size.\n"
            "The model will be downloaded to ~/.cache/huggingface/\n\n"
            "Continue?"
        )

        if not response:
            return

        # Start download in background thread
        def download_worker():
            try:
                # Use LocalTranscriber to download model
                from .local_transcriber import LocalTranscriber
                from .config import Config

                # Show progress message
                self.window.after(0, lambda: messagebox.showinfo(
                    "Downloading",
                    f"Downloading model {model_id}...\n"
                    "This window will show another message when complete.\n"
                    "Please wait, this may take several minutes."
                ))

                # Create a temporary config with the model_id to download
                # We create a new Config instance and override the local_model_id
                temp_config = Config()
                temp_config.settings['local_model_id'] = model_id
                temp_config.settings['local_model_path'] = ""  # Empty to force using model_id

                # Create transcriber with the temp config (this will trigger download)
                transcriber = LocalTranscriber(config=temp_config)

                # Test load to ensure download succeeded
                if not transcriber._load_model():
                    raise Exception("Model download or loading failed")

                # Success - update UI
                self.window.after(0, lambda: self._on_download_complete(model_id, success=True))

            except Exception as e:
                error_msg = str(e)
                self.window.after(0, lambda: self._on_download_complete(model_id, success=False, error=error_msg))

        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()

    def _on_download_complete(self, model_id, success=True, error=None):
        """Handle download completion.

        Args:
            model_id: The model ID that was downloaded
            success: Whether download succeeded
            error: Error message if failed
        """
        if success:
            messagebox.showinfo(
                "Download Complete",
                f"Model {model_id} downloaded successfully!\n\n"
                "The model is now available for use.\n"
                "Scanning for new models..."
            )
            # Refresh the model list to show the newly downloaded model
            self._scan_default_paths()
        else:
            messagebox.showerror(
                "Download Failed",
                f"Failed to download model {model_id}:\n\n{error}\n\n"
                "Please check the model ID and try again."
            )

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

            # Local STT settings
            current_config['stt_provider'] = self.entry_widgets['stt_provider'].get()
            current_config['local_engine'] = self.entry_widgets['local_engine'].get()
            current_config['local_model_path'] = self.entry_widgets['local_model_path'].get()
            current_config['local_model_id'] = self.entry_widgets['local_model_id'].get()

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
        self._update_models_list(scanning=True)

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
            self._update_models_list(scanning=True)

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
        # Merge with existing models (avoid duplicates)
        existing_paths = {model['path'] for model in self.discovered_models}
        for model in models:
            if model['path'] not in existing_paths:
                self.discovered_models.append(model)
                existing_paths.add(model['path'])

        self._update_models_list()

        if models:
            messagebox.showinfo(
                "Models Found",
                f"Found {len(models)} model(s) in this scan.\n"
                f"Total: {len(self.discovered_models)} model(s) available.\n\n"
                "Click on a model to select it."
            )
        else:
            messagebox.showinfo(
                "No Models Found",
                "No Whisper models were detected in the scanned locations.\n\n"
                "Try scanning a different folder or download a model first."
            )

    def _update_models_list(self, scanning=False):
        """Update the models listbox with discovered models.

        Args:
            scanning: If True, show "Scanning..." message
        """
        # Clear listbox
        self.models_listbox.delete(0, tk.END)

        if scanning:
            self.models_listbox.insert(tk.END, "Scanning for models... Please wait.")
        elif not self.discovered_models:
            self.models_listbox.insert(tk.END, "No models found. Click 'Scan Default Paths' or 'Scan Folder...'")
        else:
            # Add models to listbox
            for model in self.discovered_models:
                # Truncate path for display
                path = model['path']
                if len(path) > 60:
                    # Show start and end of path
                    display_path = path[:30] + "..." + path[-27:]
                else:
                    display_path = path

                display_text = f"{model['name']} - {display_path}"
                self.models_listbox.insert(tk.END, display_text)


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
