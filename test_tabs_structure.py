#!/usr/bin/env python3
"""Automated test to verify Settings window tab structure."""

import sys
from pathlib import Path
import inspect

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.settings_window import SettingsWindow

def test_settings_tabs():
    """Verify that SettingsWindow has the correct tab methods."""
    print("Testing Settings window tab structure...")

    # Check that the necessary methods exist
    methods = [
        '_create_general_tab',
        '_create_online_tab',
        '_create_local_tab'
    ]

    for method_name in methods:
        if hasattr(SettingsWindow, method_name):
            print(f"✓ Method {method_name} exists")
        else:
            print(f"✗ Method {method_name} missing!")
            return False

    # Check the show method to verify it creates three tabs
    show_source = inspect.getsource(SettingsWindow.show)

    # Verify tab creation
    if 'general_tab = ttk.Frame(notebook' in show_source:
        print("✓ General tab created")
    else:
        print("✗ General tab not found!")
        return False

    if 'online_tab = ttk.Frame(notebook' in show_source:
        print("✓ Online tab created")
    else:
        print("✗ Online tab not found!")
        return False

    if 'local_tab = ttk.Frame(notebook' in show_source:
        print("✓ Local tab created")
    else:
        print("✗ Local tab not found!")
        return False

    # Verify tab addition to notebook
    if 'notebook.add(general_tab, text="General")' in show_source:
        print("✓ General tab added with correct label")
    else:
        print("✗ General tab not properly added!")
        return False

    if 'notebook.add(online_tab, text="Online")' in show_source:
        print("✓ Online tab added with correct label")
    else:
        print("✗ Online tab not properly added!")
        return False

    if 'notebook.add(local_tab, text="Local")' in show_source:
        print("✓ Local tab added with correct label")
    else:
        print("✗ Local tab not properly added!")
        return False

    # Verify method calls
    if 'self._create_general_tab(general_tab)' in show_source:
        print("✓ _create_general_tab called")
    else:
        print("✗ _create_general_tab not called!")
        return False

    if 'self._create_online_tab(online_tab)' in show_source:
        print("✓ _create_online_tab called")
    else:
        print("✗ _create_online_tab not called!")
        return False

    if 'self._create_local_tab(local_tab)' in show_source:
        print("✓ _create_local_tab called")
    else:
        print("✗ _create_local_tab not called!")
        return False

    # Check _create_online_tab has API key field
    online_source = inspect.getsource(SettingsWindow._create_online_tab)
    if 'OpenAI API Key' in online_source:
        print("✓ Online tab contains OpenAI API Key field")
    else:
        print("✗ Online tab missing API key field!")
        return False

    # Check _create_general_tab has general settings
    general_source = inspect.getsource(SettingsWindow._create_general_tab)
    if 'STT Provider' in general_source:
        print("✓ General tab contains STT Provider")
    else:
        print("✗ General tab missing STT Provider!")
        return False

    if 'Max Recording Duration' in general_source:
        print("✓ General tab contains Max Recording Duration")
    else:
        print("✗ General tab missing Max Recording Duration!")
        return False

    if 'Audio Feedback' in general_source:
        print("✓ General tab contains Audio Feedback")
    else:
        print("✗ General tab missing Audio Feedback!")
        return False

    if 'Keyboard Shortcut' in general_source:
        print("✓ General tab contains Keyboard Shortcut")
    else:
        print("✗ General tab missing Keyboard Shortcut!")
        return False

    if 'Start at Login' in general_source:
        print("✓ General tab contains Start at Login")
    else:
        print("✗ General tab missing Start at Login!")
        return False

    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("Settings window correctly implements three tabs:")
    print("  1. General - STT provider, duration, feedback, shortcut, autostart")
    print("  2. Online - OpenAI API configuration")
    print("  3. Local - Local STT configuration")
    return True

if __name__ == "__main__":
    success = test_settings_tabs()
    sys.exit(0 if success else 1)
