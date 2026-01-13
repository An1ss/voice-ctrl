#!/usr/bin/env python3
"""Test script to verify tray icon menu fix for US-016."""

import sys
import time
import threading
from src.tray_icon import TrayIcon

# Track which menu items were clicked
clicks = {"settings": 0, "about": 0, "quit": 0}

def test_settings():
    """Test settings callback."""
    clicks["settings"] += 1
    print(f"✓ Settings menu item clicked! (count: {clicks['settings']})")

def test_about():
    """Test about callback."""
    clicks["about"] += 1
    print(f"✓ About menu item clicked! (count: {clicks['about']})")

def test_quit():
    """Test quit callback."""
    clicks["quit"] += 1
    print(f"✓ Quit menu item clicked! (count: {clicks['quit']})")
    print("\nQuitting...")
    sys.exit(0)

print("=" * 60)
print("US-016 Menu Fix Test")
print("=" * 60)

# Create tray icon with all three menu callbacks
tray = TrayIcon(
    tooltip="Voice Control - Menu Test",
    on_settings=test_settings,
    on_about=test_about,
    on_quit=test_quit
)

# Verify menu is created correctly
menu_func = tray._create_menu()
if menu_func:
    items = menu_func(None)
    print(f"\n✓ Menu created successfully with {len(items)} items:")
    for item in items:
        print(f"  - {item.text}")
else:
    print("\n✗ ERROR: Menu not created!")
    sys.exit(1)

# Start the tray icon
print("\nStarting tray icon...")
tray.start()

# Wait a moment for icon to initialize
time.sleep(1)

if tray.icon and tray.tray_thread.is_alive():
    print("✓ Tray icon started successfully")
    print("\n" + "=" * 60)
    print("MANUAL TEST INSTRUCTIONS:")
    print("=" * 60)
    print("1. Look for the tray icon in your system tray")
    print("2. RIGHT-CLICK the icon (or left-click on some systems)")
    print("3. Verify you see a menu with 3 items:")
    print("   - Settings")
    print("   - About")
    print("   - Quit")
    print("4. Click each menu item to test (Quit will exit)")
    print("\nPress Ctrl+C to exit without testing Quit")
    print("=" * 60)
else:
    print("✗ ERROR: Tray icon failed to start!")
    sys.exit(1)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nTest stopped by user")
    print(f"\nMenu item click counts:")
    print(f"  Settings: {clicks['settings']}")
    print(f"  About: {clicks['about']}")
    print(f"  Quit: {clicks['quit']}")
    print("\nStopping tray icon...")
    tray.stop()
    print("✓ Test complete")
