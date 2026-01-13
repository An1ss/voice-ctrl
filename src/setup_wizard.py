"""Setup wizard module for first-time VoiceControl configuration."""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import webbrowser
from pathlib import Path
from openai import OpenAI
from openai import AuthenticationError, APIError, APIConnectionError


def validate_api_key(api_key):
    """Validate OpenAI API key by making a test request.

    Args:
        api_key: The API key string to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not api_key or not api_key.strip():
        return False, "API key cannot be empty"

    try:
        # Initialize OpenAI client with the key
        client = OpenAI(api_key=api_key.strip(), timeout=10.0)

        # Make a minimal test request to validate the key
        # Using models.list() is a lightweight way to verify authentication
        models = client.models.list()

        # If we got here, the API key is valid
        return True, None

    except AuthenticationError as e:
        return False, "Invalid API key. Please check your key and try again."

    except APIConnectionError as e:
        return False, "Network connection error. Please check your internet connection."

    except APIError as e:
        return False, f"API error: {str(e)}"

    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


class SetupWizard:
    """First-time setup wizard for configuring the OpenAI API key."""

    def __init__(self, config_path):
        """Initialize the setup wizard.

        Args:
            config_path: Path to the config file
        """
        self.config_path = Path(config_path)
        self.api_key = ""
        self.window = None
        self.api_key_entry = None
        self.status_label = None
        self.validate_button = None
        self.save_button = None

    def show(self):
        """Show the setup wizard window and return the API key.

        Returns:
            API key string if successfully configured, None if cancelled
        """
        # Create window
        self.window = tk.Tk()
        self.window.title("Voice Control - First Time Setup")
        self.window.geometry("550x550")
        self.window.resizable(False, False)

        # Make window modal
        self.window.grab_set()

        # Create main frame with padding
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Welcome title
        title_label = ttk.Label(
            main_frame,
            text="Welcome to Voice Control!",
            font=("", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="To use Voice Control, you need an OpenAI API key.\n"
                 "This is required to transcribe your speech using the Whisper API.",
            justify=tk.LEFT,
            wraplength=490
        )
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Instructions
        instructions_label = ttk.Label(
            main_frame,
            text="1. Click 'Get API Key' to open the OpenAI website\n"
                 "2. Sign in or create an account\n"
                 "3. Generate a new API key\n"
                 "4. Copy and paste it below\n"
                 "5. Click 'Validate & Save'",
            justify=tk.LEFT,
            font=("", 9)
        )
        instructions_label.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)

        # Get API Key button
        get_key_button = ttk.Button(
            main_frame,
            text="Get API Key",
            command=self._open_api_key_url
        )
        get_key_button.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        # API Key input
        api_key_label = ttk.Label(main_frame, text="OpenAI API Key:")
        api_key_label.grid(row=4, column=0, sticky=tk.W, pady=5)

        self.api_key_entry = ttk.Entry(main_frame, width=50, show="*")
        self.api_key_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Show/Hide password checkbox
        show_password_var = tk.BooleanVar(value=False)
        show_password_check = ttk.Checkbutton(
            main_frame,
            text="Show API key",
            variable=show_password_var,
            command=lambda: self._toggle_password_visibility(show_password_var.get())
        )
        show_password_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Status label (for validation feedback)
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=("", 9),
            foreground="gray"
        )
        self.status_label.grid(row=7, column=0, columnspan=2, pady=(0, 10))

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))

        # Validate & Save button
        self.save_button = ttk.Button(
            button_frame,
            text="Validate & Save",
            command=self._validate_and_save
        )
        self.save_button.grid(row=0, column=0, padx=5)

        # Skip button
        skip_button = ttk.Button(
            button_frame,
            text="Skip (Configure Later)",
            command=self._skip_setup
        )
        skip_button.grid(row=0, column=1, padx=5)

        # Focus on API key entry
        self.api_key_entry.focus()

        # Bind Enter key to validate and save
        self.api_key_entry.bind('<Return>', lambda e: self._validate_and_save())

        # Handle window close (same as skip)
        self.window.protocol("WM_DELETE_WINDOW", self._skip_setup)

        # Run the window and wait for it to close
        self.window.mainloop()

        return self.api_key

    def _open_api_key_url(self):
        """Open the OpenAI API keys page in the default browser."""
        try:
            webbrowser.open("https://platform.openai.com/api-keys")
            self._update_status("Opening browser...", "blue")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to open browser:\n{str(e)}\n\n"
                "Please manually visit: https://platform.openai.com/api-keys"
            )

    def _toggle_password_visibility(self, show):
        """Toggle API key visibility.

        Args:
            show: True to show the key, False to hide it
        """
        if show:
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def _update_status(self, message, color="gray"):
        """Update the status label.

        Args:
            message: Status message to display
            color: Text color (gray, blue, green, red)
        """
        if self.status_label:
            self.status_label.config(text=message, foreground=color)

    def _validate_and_save(self):
        """Validate the API key and save if valid."""
        api_key = self.api_key_entry.get().strip()

        if not api_key:
            self._update_status("Please enter an API key", "red")
            return

        # Disable button during validation
        self.save_button.config(state="disabled")
        self._update_status("Validating API key...", "blue")
        self.window.update()

        # Validate the API key
        is_valid, error_message = validate_api_key(api_key)

        if is_valid:
            # Save to config file
            try:
                self._save_to_config(api_key)
                self._update_status("API key validated and saved successfully!", "green")
                self.api_key = api_key

                # Show success message
                messagebox.showinfo(
                    "Setup Complete",
                    "Your API key has been validated and saved!\n\n"
                    "Voice Control is now ready to use."
                )

                # Close the window
                self.window.destroy()

            except Exception as e:
                self._update_status(f"Error saving config: {str(e)}", "red")
                self.save_button.config(state="normal")
                messagebox.showerror(
                    "Save Failed",
                    f"Failed to save configuration:\n{str(e)}"
                )
        else:
            # Show error
            self._update_status(f"Validation failed: {error_message}", "red")
            self.save_button.config(state="normal")
            messagebox.showerror(
                "Validation Failed",
                error_message
            )

    def _save_to_config(self, api_key):
        """Save the API key to the config file.

        Args:
            api_key: The validated API key to save
        """
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing config or create new one
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {
                "max_duration_seconds": 240,
                "audio_feedback_enabled": True,
                "keyboard_shortcut": "Ctrl+Shift+Space"
            }

        # Update API key
        config["api_key"] = api_key

        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def _skip_setup(self):
        """Skip the setup wizard."""
        result = messagebox.askyesno(
            "Skip Setup",
            "Are you sure you want to skip setup?\n\n"
            "Voice Control will not work without an API key.\n"
            "You can configure it later from the Settings menu.",
            icon='warning'
        )

        if result:
            self.api_key = None
            self.window.destroy()


def should_show_setup_wizard(config):
    """Check if the setup wizard should be shown on startup.

    Args:
        config: Config object

    Returns:
        True if setup wizard should be shown, False otherwise
    """
    api_key = config.get_api_key()

    # Show wizard if no API key is configured
    if not api_key or not api_key.strip():
        return True

    return False
