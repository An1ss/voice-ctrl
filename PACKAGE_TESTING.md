# VoiceControl .deb Package Testing Guide

This document describes how to test the voice-ctrl.deb package installation.

## Pre-Installation Verification

1. **Check package info**:
   ```bash
   dpkg-deb --info voice-ctrl.deb
   ```
   - Verify version is 1.0.0
   - Check dependencies are listed correctly

2. **Check package contents**:
   ```bash
   dpkg-deb --contents voice-ctrl.deb
   ```
   - Verify files are in correct locations

## Installation Testing

1. **Install the package**:
   ```bash
   sudo dpkg -i voice-ctrl.deb
   ```

2. **Install dependencies if needed**:
   ```bash
   sudo apt-get install -f
   ```

3. **Verify installation**:
   ```bash
   # Check files were installed
   ls -la /opt/voice-ctrl/
   ls -la /usr/bin/voice-ctrl
   ls -la /usr/share/applications/voice-ctrl.desktop
   ls -la /usr/share/pixmaps/voice-ctrl.png

   # Check virtual environment was created
   ls -la /opt/voice-ctrl/venv/

   # Check Python packages were installed
   /opt/voice-ctrl/venv/bin/pip list | grep -E "(openai|pynput|sounddevice)"
   ```

## Functionality Testing

1. **Launch from terminal**:
   ```bash
   voice-ctrl
   ```
   - Should start the application
   - Should show "VoiceControl started!" message
   - Tray icon should appear

2. **Launch from application menu**:
   - Open application launcher (Super key)
   - Search for "VoiceControl"
   - Click to launch
   - Verify tray icon appears

3. **Test setup wizard**:
   - On first launch, setup wizard should appear
   - "Get API Key" button should open browser
   - Can enter API key and validate
   - Can skip setup

4. **Test configuration**:
   - Check config directory exists: `ls ~/.config/voice-ctrl/`
   - Config file should exist: `cat ~/.config/voice-ctrl/config.json`
   - Should contain all default parameters

5. **Test tray icon menu**:
   - Click on tray icon
   - Verify menu appears with: View History, Settings, About, Quit
   - Test each menu item opens correct window

6. **Test settings window**:
   - Open Settings from tray menu
   - Verify all settings are displayed
   - Try changing a setting and saving
   - Verify config file is updated

7. **Test recording** (requires valid API key):
   - Press Ctrl+Shift+Space (default shortcut)
   - Speak something
   - Press Ctrl+Shift+Space again
   - Verify text is transcribed and pasted

## Uninstallation Testing

1. **Uninstall the package**:
   ```bash
   sudo apt remove voice-ctrl
   ```

2. **Verify files removed**:
   ```bash
   # These should not exist
   ls /opt/voice-ctrl/  # Should be gone
   ls /usr/bin/voice-ctrl  # Should be gone
   ls /usr/share/applications/voice-ctrl.desktop  # Should be gone

   # User config should still exist (preserved)
   ls ~/.config/voice-ctrl/  # Should still exist
   ```

3. **Test purge** (removes config):
   ```bash
   sudo apt purge voice-ctrl
   ```

## Expected Results

### Installation
- ✓ Package installs without errors
- ✓ All dependencies are satisfied
- ✓ Virtual environment is created at /opt/voice-ctrl/venv
- ✓ Python packages are installed in venv
- ✓ Launcher script is executable
- ✓ Desktop file is installed
- ✓ Icon is installed

### Functionality
- ✓ Can launch from terminal with `voice-ctrl` command
- ✓ Can launch from application menu
- ✓ Tray icon appears after launch
- ✓ Setup wizard appears on first launch
- ✓ Config directory is created
- ✓ All menu items work
- ✓ Settings window opens and saves changes
- ✓ Recording works with valid API key

### Uninstallation
- ✓ Package removes cleanly
- ✓ Application files are removed from /opt
- ✓ Launcher is removed from /usr/bin
- ✓ Desktop file is removed
- ✓ User config is preserved (unless purge)

## Common Issues

### Issue: dpkg dependency errors
**Solution**: Run `sudo apt-get install -f` to install missing dependencies

### Issue: Virtual environment creation fails
**Solution**: Ensure python3-venv is installed: `sudo apt install python3-venv`

### Issue: Application doesn't appear in menu
**Solution**: Update desktop database: `sudo update-desktop-database`

### Issue: Icon doesn't show
**Solution**: Icon should be at /usr/share/pixmaps/voice-ctrl.png, verify it exists

## Testing Checklist

- [ ] Package info shows correct version and dependencies
- [ ] Package contents include all required files
- [ ] Installation completes without errors
- [ ] Virtual environment is created
- [ ] Python dependencies are installed
- [ ] Can launch from terminal
- [ ] Can launch from application menu
- [ ] Tray icon appears
- [ ] Setup wizard appears on first launch
- [ ] Config directory is created
- [ ] Tray menu works
- [ ] Settings window works
- [ ] Recording works (with API key)
- [ ] Uninstallation removes files cleanly
- [ ] User config is preserved after removal
