"""Text pasting module using clipboard and keyboard simulation."""

import time
import pyperclip
from pynput.keyboard import Controller, Key


class TextPaster:
    """Pastes text at cursor position using clipboard and Ctrl+V simulation."""

    def __init__(self, restore_clipboard=True, paste_delay=0.1):
        """Initialize the text paster.

        Args:
            restore_clipboard: Whether to restore previous clipboard contents after pasting
            paste_delay: Delay in seconds between clipboard copy and Ctrl+V (default 0.1)
        """
        self.restore_clipboard = restore_clipboard
        self.paste_delay = paste_delay
        self.keyboard = Controller()

    def paste_text(self, text):
        """Paste text at current cursor position.

        Args:
            text: String to paste at cursor position

        Returns:
            True if paste was successful, False otherwise
        """
        # Handle edge case: empty or None text
        if not text:
            print("WARNING: No text to paste (empty or None)")
            return False

        try:
            # Save previous clipboard contents if restore is enabled
            previous_clipboard = None
            if self.restore_clipboard:
                try:
                    previous_clipboard = pyperclip.paste()
                except Exception as e:
                    print(f"WARNING: Could not read previous clipboard contents: {e}")
                    # Continue anyway, just won't restore clipboard

            # Copy transcribed text to clipboard
            pyperclip.copy(text)
            print(f"Copied text to clipboard: {text[:100]}..." if len(text) > 100 else f"Copied text to clipboard: {text}")

            # Wait for clipboard to be ready
            time.sleep(self.paste_delay)

            # Simulate Ctrl+V keystroke
            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press('v')
                self.keyboard.release('v')

            print("Simulated Ctrl+V keystroke")

            # Optional: wait a bit before restoring clipboard to ensure paste completes
            if self.restore_clipboard and previous_clipboard is not None:
                time.sleep(0.1)
                try:
                    pyperclip.copy(previous_clipboard)
                    print("Restored previous clipboard contents")
                except Exception as e:
                    print(f"WARNING: Could not restore previous clipboard contents: {e}")

            return True

        except Exception as e:
            print(f"ERROR: Failed to paste text: {e}")
            return False
