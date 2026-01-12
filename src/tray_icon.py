"""System tray icon module for VoiceControl application."""

import pystray
from PIL import Image, ImageDraw
import threading


class TrayIcon:
    """Manages system tray icon with state indicators."""

    def __init__(self, tooltip="Voice Control"):
        """Initialize the tray icon.

        Args:
            tooltip: Tooltip text shown on hover
        """
        self.tooltip = tooltip
        self.icon = None
        self.is_recording = False
        self.tray_thread = None

        # Generate icon images
        self.idle_icon = self._create_idle_icon()
        self.recording_icon = self._create_recording_icon()

    def _create_idle_icon(self):
        """Create gray microphone icon for idle state.

        Returns:
            PIL Image object
        """
        # Create 64x64 image with transparent background
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw gray microphone shape
        # Microphone body (rounded rectangle)
        draw.ellipse([20, 15, 44, 35], fill='gray', outline='darkgray', width=2)
        draw.rectangle([20, 25, 44, 40], fill='gray', outline='darkgray')
        draw.ellipse([20, 35, 44, 45], fill='gray', outline='darkgray', width=2)

        # Microphone stand
        draw.line([32, 45, 32, 52], fill='darkgray', width=2)
        draw.arc([24, 40, 40, 52], 0, 180, fill='darkgray', width=2)

        # Base
        draw.rectangle([24, 52, 40, 55], fill='gray')

        return image

    def _create_recording_icon(self):
        """Create red microphone icon for recording state.

        Returns:
            PIL Image object
        """
        # Create 64x64 image with transparent background
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw red microphone shape (same as idle but red)
        # Microphone body (rounded rectangle)
        draw.ellipse([20, 15, 44, 35], fill='red', outline='darkred', width=2)
        draw.rectangle([20, 25, 44, 40], fill='red', outline='darkred')
        draw.ellipse([20, 35, 44, 45], fill='red', outline='darkred', width=2)

        # Microphone stand
        draw.line([32, 45, 32, 52], fill='darkred', width=2)
        draw.arc([24, 40, 40, 52], 0, 180, fill='darkred', width=2)

        # Base
        draw.rectangle([24, 52, 40, 55], fill='red')

        return image

    def start(self):
        """Start the system tray icon in a separate thread."""
        if self.tray_thread and self.tray_thread.is_alive():
            print("Tray icon already running!")
            return

        # Create icon with idle state
        self.icon = pystray.Icon(
            "voice_control",
            self.idle_icon,
            self.tooltip
        )

        # Run icon in separate thread to avoid blocking
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()

        print("System tray icon started")

    def stop(self):
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()
            print("System tray icon stopped")

    def set_recording_state(self, is_recording):
        """Update icon based on recording state.

        Args:
            is_recording: True if recording, False if idle
        """
        if not self.icon:
            return

        self.is_recording = is_recording

        # Update icon image based on state
        if is_recording:
            self.icon.icon = self.recording_icon
        else:
            self.icon.icon = self.idle_icon

        print(f"Tray icon state: {'recording' if is_recording else 'idle'}")
