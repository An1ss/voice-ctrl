"""History viewer window module for VoiceControl application."""

import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import threading


class HistoryWindow:
    """Manages the history viewer GUI window."""

    def __init__(self, history_manager):
        """Initialize the history viewer window.

        Args:
            history_manager: HistoryManager instance containing transcription history
        """
        self.history_manager = history_manager
        self.window = None

    def show(self):
        """Show the history viewer window."""
        if self.window is not None:
            # Window already exists, bring it to front
            self.window.lift()
            self.window.focus_force()
            return

        # Create new window
        self.window = tk.Tk()
        self.window.title("Transcription History")
        self.window.geometry("700x500")
        self.window.resizable(True, True)

        # Configure window grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=0)
        self.window.rowconfigure(1, weight=1)
        self.window.rowconfigure(2, weight=0)

        # Title frame
        title_frame = ttk.Frame(self.window, padding="15")
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        title_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            title_frame,
            text="Transcription History",
            font=("", 14, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Entry count
        entry_count = self.history_manager.get_entry_count()
        count_label = ttk.Label(
            title_frame,
            text=f"{entry_count} entries (last 30)",
            font=("", 10),
            foreground="gray"
        )
        count_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Create scrollable frame for history entries
        entries_frame = ttk.Frame(self.window)
        entries_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=(0, 15))
        entries_frame.columnconfigure(0, weight=1)
        entries_frame.rowconfigure(0, weight=1)

        # Create canvas with scrollbar
        canvas = tk.Canvas(entries_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(entries_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        entries_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(0, weight=1)

        # Populate history entries
        entries = self.history_manager.get_entries()
        if not entries:
            # Show empty state
            empty_label = ttk.Label(
                scrollable_frame,
                text="No transcription history yet.\n\nRecord some audio to see your transcriptions here.",
                justify=tk.CENTER,
                foreground="gray",
                font=("", 11)
            )
            empty_label.grid(row=0, column=0, pady=50)
        else:
            # Add each history entry
            for idx, entry in enumerate(entries):
                self._create_entry_widget(scrollable_frame, entry, idx)

        # Button frame
        button_frame = ttk.Frame(self.window, padding="15")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        # Clear History button
        clear_button = ttk.Button(
            button_frame,
            text="Clear History",
            command=self._clear_history,
            width=15
        )
        clear_button.pack(side=tk.LEFT, padx=5)

        # Close button
        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self._close_window,
            width=12
        )
        close_button.pack(side=tk.RIGHT, padx=5)

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        # Run the window
        self.window.mainloop()

    def _create_entry_widget(self, parent, entry, index):
        """Create a widget for a single history entry.

        Args:
            parent: Parent frame to add widget to
            entry: Dictionary containing history entry data
            index: Index of the entry in the list
        """
        # Entry frame with border
        entry_frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding="10")
        entry_frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=5)
        entry_frame.columnconfigure(0, weight=1)

        # Header frame (timestamp and duration)
        header_frame = ttk.Frame(entry_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header_frame.columnconfigure(1, weight=1)

        # Timestamp
        timestamp_label = ttk.Label(
            header_frame,
            text=entry['timestamp'],
            font=("", 9, "bold")
        )
        timestamp_label.grid(row=0, column=0, sticky=tk.W)

        # Duration
        duration_text = f"{entry['duration_seconds']:.1f}s"
        duration_label = ttk.Label(
            header_frame,
            text=duration_text,
            font=("", 9),
            foreground="gray"
        )
        duration_label.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))

        # Transcribed text
        text_widget = tk.Text(
            entry_frame,
            wrap=tk.WORD,
            height=3,
            font=("", 10),
            relief="flat",
            background="#f5f5f5",
            padx=5,
            pady=5
        )
        text_widget.insert("1.0", entry['text'])
        text_widget.configure(state="disabled")  # Make read-only
        text_widget.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 8))

        # Copy button
        copy_button = ttk.Button(
            entry_frame,
            text="Copy to Clipboard",
            command=lambda: self._copy_to_clipboard(entry['text']),
            width=18
        )
        copy_button.grid(row=2, column=0, sticky=tk.E)

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard.

        Args:
            text: Text to copy
        """
        try:
            pyperclip.copy(text)
            messagebox.showinfo(
                "Copied",
                "Text copied to clipboard!"
            )
        except Exception as e:
            messagebox.showerror(
                "Copy Failed",
                f"Failed to copy to clipboard:\n{str(e)}"
            )

    def _clear_history(self):
        """Clear all history entries."""
        # Confirm with user
        result = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all transcription history?\n\n"
            "This action cannot be undone.",
            icon=messagebox.WARNING
        )

        if result:
            self.history_manager.clear_history()
            messagebox.showinfo(
                "History Cleared",
                "All transcription history has been cleared."
            )
            # Close and reopen window to show empty state
            self._close_window()
            # Reopen in a thread to avoid blocking
            threading.Thread(target=self.show, daemon=True).start()

    def _close_window(self):
        """Close the history viewer window."""
        if self.window:
            self.window.destroy()
            self.window = None
