"""System tray icon module for VoiceControl application."""

import sys
from PIL import Image, ImageDraw
import threading

# Try to use AppIndicator backend for better GNOME Shell support
try:
    from pystray import _appindicator as pystray_backend
    from pystray import MenuItem as Item, Menu
    BACKEND = "appindicator"
except ImportError:
    # Fallback to X11 backend
    from pystray import _xorg as pystray_backend
    from pystray import MenuItem as Item, Menu
    BACKEND = "xorg"


class TrayIcon:
    """Manages system tray icon with state indicators."""

    def __init__(self, tooltip="Voice Control", on_settings=None, on_about=None, on_quit=None, on_view_history=None):
        """Initialize the tray icon.

        Args:
            tooltip: Tooltip text shown on hover
            on_settings: Callback function for Settings menu item
            on_about: Callback function for About menu item
            on_quit: Callback function for Quit menu item
            on_view_history: Callback function for View History menu item
        """
        self.tooltip = tooltip
        self.icon = None
        self.is_recording = False
        self.tray_thread = None
        self.on_settings = on_settings
        self.on_about = on_about
        self.on_quit = on_quit
        self.on_view_history = on_view_history

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

    def _create_menu(self):
        """Create the tray icon menu with dynamic item generation.

        Returns:
            Menu object with callable for AppIndicator compatibility
        """
        def menu_builder():
            """Build menu items dynamically on each click."""
            items = []

            # View History menu item
            if self.on_view_history:
                items.append(Item("View History", self._handle_view_history))

            # Settings menu item
            if self.on_settings:
                items.append(Item("Settings", self._handle_settings))

            # About menu item
            if self.on_about:
                items.append(Item("About", self._handle_about))

            # Quit menu item
            if self.on_quit:
                items.append(Item("Quit", self._handle_quit))

            return items

        # Return Menu object wrapping the callable for dynamic menu generation
        return Menu(menu_builder)

    def _handle_view_history(self, icon, item):
        """Handle View History menu click."""
        if self.on_view_history:
            # Run in separate thread to avoid blocking the tray icon
            threading.Thread(target=self.on_view_history, daemon=True).start()

    def _handle_settings(self, icon, item):
        """Handle Settings menu click."""
        if self.on_settings:
            # Run in separate thread to avoid blocking the tray icon
            threading.Thread(target=self.on_settings, daemon=True).start()

    def _handle_about(self, icon, item):
        """Handle About menu click."""
        if self.on_about:
            # Run in separate thread to avoid blocking the tray icon
            threading.Thread(target=self.on_about, daemon=True).start()

    def _handle_quit(self, icon, item):
        """Handle Quit menu click."""
        # Stop the icon first to remove it from tray
        icon.stop()
        # Then call the quit callback
        if self.on_quit:
            # Run quit in a thread to ensure icon.stop() completes first
            threading.Thread(target=self.on_quit, daemon=False).start()

    def start(self):
        """Start the system tray icon in a separate thread."""
        if self.tray_thread and self.tray_thread.is_alive():
            print("Tray icon already running!")
            return

        # Create menu
        menu = self._create_menu()

        # Create icon with idle state and menu
        # Note: title parameter sets the tooltip text shown on hover
        # On GNOME Shell/AppIndicator, the menu appears on click (left or right)
        self.icon = pystray_backend.Icon(
            name="voice_control",
            icon=self.idle_icon,
            title=self.tooltip,
            menu=menu
        )

        # Run icon in separate thread to avoid blocking
        # The icon.run() method makes the icon visible and sets up the menu
        def run_icon():
            try:
                self.icon.run()
            except Exception as e:
                print(f"ERROR: System tray icon failed: {e}")
                import traceback
                traceback.print_exc()

        self.tray_thread = threading.Thread(target=run_icon, daemon=True)
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
