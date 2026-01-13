"""System tray icon module for VoiceControl application."""

import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image, ImageDraw
import threading


class TrayIcon:
    """Manages system tray icon with state indicators."""

    def __init__(self, tooltip="Voice Control", on_settings=None, on_about=None, on_quit=None):
        """Initialize the tray icon.

        Args:
            tooltip: Tooltip text shown on hover
            on_settings: Callback function for Settings menu item
            on_about: Callback function for About menu item
            on_quit: Callback function for Quit menu item
        """
        self.tooltip = tooltip
        self.icon = None
        self.is_recording = False
        self.tray_thread = None
        self.on_settings = on_settings
        self.on_about = on_about
        self.on_quit = on_quit

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
        """Create the tray icon menu as a callable.

        Returns:
            Callable that returns menu items (for dynamic menu support)
        """
        def menu_builder(icon):
            """Build menu items dynamically."""
            items = []

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
        # This ensures menu works properly on Linux with AppIndicator
        return Menu(menu_builder) if (self.on_settings or self.on_about or self.on_quit) else None

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
        if self.on_quit:
            self.on_quit()
        # Stop the icon
        icon.stop()

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
        self.icon = pystray.Icon(
            name="voice_control",
            icon=self.idle_icon,
            title=self.tooltip,
            menu=menu
        )

        # Run icon in separate thread to avoid blocking
        # The icon.run() method makes the icon visible and sets up the menu
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
