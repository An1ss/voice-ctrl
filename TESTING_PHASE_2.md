# Testing Plan - Phase 2 Features

Testing plan for newly implemented features: Transcription History, .deb Package, and Autostart Support.

**Date:** 2026-01-13
**Phase:** Phase 2 (US-019, US-020, US-021)

---

## Pre-Testing Setup

Before testing, ensure:
- [ ] Phase 1 features are working (basic voice recording and transcription)
- [ ] You have a valid OpenAI API key configured
- [ ] Git repository is up to date: `git pull origin master`

---

## US-019: Transcription History Log

**Feature:** Store last 30 transcriptions with timestamp and allow viewing from tray menu.

### Test 1: History File Creation

**Steps:**
1. Check if history file exists: `ls -la ~/.config/voice-ctrl/history.json`
2. If it exists, check its contents: `cat ~/.config/voice-ctrl/history.json`

**Expected:**
- File exists at `~/.config/voice-ctrl/history.json`
- File is valid JSON (empty array `[]` or contains transcription entries)

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 2: Recording Transcriptions to History

**Steps:**
1. Run the app: `source venv/bin/activate && python -m src.main`
2. Make 3 test transcriptions:
   - Press `Ctrl+Shift+Space`, say "This is test one", press shortcut again
   - Wait for transcription to complete
   - Repeat with "This is test two"
   - Repeat with "This is test three"
3. Check history file: `cat ~/.config/voice-ctrl/history.json | jq '.'`

**Expected:**
- History file contains 3 entries
- Each entry has: `timestamp`, `text`, `duration_seconds`
- Timestamps are in ISO format (e.g., "2026-01-13T14:30:25")
- Text matches what was spoken
- Duration is approximately correct (in seconds)

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 3: View History from Tray Menu

**Steps:**
1. Ensure app is running
2. Click on the tray icon
3. Look for "View History" menu item
4. Click "View History"
5. Verify history window appears

**Expected:**
- Tray menu has "View History" option (should be between "Settings" and "About")
- Clicking opens a new window titled "Transcription History"
- Window shows scrollable list of recent transcriptions
- Each entry shows: timestamp, text snippet, duration
- Most recent transcription is at the top

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 4: Copy from History

**Steps:**
1. Open View History window
2. Select a transcription entry
3. Click "Copy" button (or double-click entry if that's the interaction)
4. Paste into a text editor with `Ctrl+V` or `Shift+Insert`

**Expected:**
- Selected transcription text is copied to clipboard
- Pasting shows the full transcription text
- Copy action provides visual feedback (if implemented)

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 5: History Limit (30 entries)

**Steps:**
1. Check current history count: `cat ~/.config/voice-ctrl/history.json | jq 'length'`
2. If less than 30 entries, make additional recordings until you reach 30+
3. Make 5 more transcriptions (total should be 35+)
4. Check history again: `cat ~/.config/voice-ctrl/history.json | jq 'length'`

**Expected:**
- History file contains exactly 30 entries (oldest removed)
- Newest entries are preserved
- File size doesn't grow unbounded

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

## US-020: Create .deb Package for Easy Installation

**Feature:** Installable .deb package with all dependencies and desktop launcher.

### Test 1: Package Build

**Steps:**
1. Check if build script exists: `ls -la scripts/build-deb.sh` or similar
2. Check if .deb package was created: `ls -la *.deb`
3. Check package name and version

**Expected:**
- Build script exists (or package was built by Ralph)
- .deb file exists (e.g., `voice-ctrl_1.0.0_amd64.deb` or similar)
- Package name follows Debian naming conventions

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 2: Package Installation

**Steps:**
1. If currently running from source, stop the app
2. Install the package: `sudo dpkg -i voice-ctrl*.deb`
3. Check for dependency errors: `sudo apt-get install -f` (if needed)
4. Verify installation: `dpkg -l | grep voice-ctrl`

**Expected:**
- Package installs without errors
- All dependencies are satisfied (or auto-installed)
- Package shows as installed in dpkg

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 3: Launch from Application Menu

**Steps:**
1. Open application launcher (press Super key)
2. Search for "Voice Control" or "VoiceControl"
3. Click the application icon
4. Verify app starts

**Expected:**
- App appears in application menu with proper icon
- Clicking launches the application
- Tray icon appears after launch
- No terminal window appears

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 4: Command Line Launcher

**Steps:**
1. Open terminal
2. Run: `voice-ctrl`
3. Verify app starts

**Expected:**
- Command is found in PATH
- App launches successfully
- Tray icon appears
- Terminal can be closed without stopping the app

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 5: Verify Installation Paths

**Steps:**
1. Check installation location: `which voice-ctrl`
2. Check application files: `dpkg -L voice-ctrl` (lists all installed files)
3. Verify desktop file: `cat /usr/share/applications/voice-ctrl.desktop`

**Expected:**
- Launcher script in `/usr/bin/voice-ctrl`
- Application files in `/opt/voice-ctrl/` or `/usr/share/voice-ctrl/`
- Desktop file exists with correct Exec path and Icon
- Config directory created at `~/.config/voice-ctrl/`

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 6: Package Uninstallation

**Steps:**
1. Stop the app if running
2. Uninstall: `sudo apt remove voice-ctrl` or `sudo dpkg -r voice-ctrl`
3. Verify removal: `dpkg -l | grep voice-ctrl`
4. Check if files remain: `ls /usr/bin/voice-ctrl` (should not exist)

**Expected:**
- Package uninstalls cleanly
- No errors during removal
- Launcher and application files removed
- Config directory `~/.config/voice-ctrl/` preserved (user data)

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

## US-021: Add Desktop Autostart Support

**Feature:** "Start at Login" checkbox in Settings window.

### Test 1: Autostart Checkbox in Settings

**Steps:**
1. Run the app (from package or source)
2. Click tray icon → Settings
3. Look for "Start at Login" checkbox

**Expected:**
- Settings window has "Start at Login" checkbox
- Checkbox is visible and not cut off
- Checkbox state reflects current autostart status
- Checkbox has clear label

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 2: Enable Autostart

**Steps:**
1. Open Settings window
2. Check "Start at Login" checkbox
3. Click "Save"
4. Check if autostart file created: `ls ~/.config/autostart/voice-ctrl.desktop`
5. View autostart file: `cat ~/.config/autostart/voice-ctrl.desktop`

**Expected:**
- Checkbox can be enabled
- Autostart file created at `~/.config/autostart/voice-ctrl.desktop`
- Desktop file contains:
  - `Hidden=false`
  - `X-GNOME-Autostart-enabled=true`
  - Correct `Exec` path
- Save confirmation shows success message

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 3: Autostart After Login

**Steps:**
1. Enable "Start at Login" in Settings
2. Log out of your session
3. Log back in
4. Wait 5-10 seconds after login

**Expected:**
- VoiceControl starts automatically after login
- Tray icon appears without manual launch
- No terminal window appears
- App is fully functional (can record/transcribe)

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 4: Disable Autostart

**Steps:**
1. Open Settings window
2. Uncheck "Start at Login" checkbox
3. Click "Save"
4. Check if autostart file removed: `ls ~/.config/autostart/voice-ctrl.desktop`

**Expected:**
- Checkbox can be unchecked
- Autostart file is deleted
- Save confirmation shows success message
- Next login will not auto-start the app

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

### Test 5: Autostart Persistence

**Steps:**
1. Enable autostart
2. Reboot system (or log out/in)
3. After login, open Settings
4. Check "Start at Login" checkbox state

**Expected:**
- Autostart persists across reboots
- Settings checkbox reflects actual autostart state
- No duplicate autostart entries

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

## Integration Tests

### Test 1: All Features Together

**Steps:**
1. Install from .deb package
2. Launch from application menu
3. Enable autostart
4. Make 5 transcriptions
5. View history
6. Reboot
7. Verify app auto-started
8. Make more transcriptions
9. Check history includes all entries

**Expected:**
- All features work together seamlessly
- No conflicts or errors
- History persists across restarts
- Autostart works reliably

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

## Regression Tests (Phase 1 Features)

Verify Phase 1 features still work after Phase 2 changes:

### Quick Regression Checklist

- [ ] Recording starts/stops with keyboard shortcut
- [ ] Audio beep plays on start/stop
- [ ] Transcription works correctly
- [ ] Text pastes at cursor position
- [ ] Tray icon shows idle/recording states
- [ ] Settings window opens and saves changes
- [ ] About dialog displays correctly
- [ ] Error notifications appear when appropriate
- [ ] Setup wizard appears on first run (test with fresh config)

**Result:** ☐ Pass / ☐ Fail

**Notes:**


---

## Summary

**Test Date:** _______________

**Tester:** _______________

**Results:**
- US-019 Tests Passed: _____ / 5
- US-020 Tests Passed: _____ / 6
- US-021 Tests Passed: _____ / 5
- Integration Tests: _____ / 1
- Regression Tests: _____ / 1

**Total:** _____ / 18

---

## Issues Found

| Issue ID | Description | Severity | Story | Status |
|----------|-------------|----------|-------|--------|
| P2-001   |             |          |       |        |
| P2-002   |             |          |       |        |
| P2-003   |             |          |       |        |

**Severity Levels:**
- Critical: Blocks core functionality
- High: Major feature broken
- Medium: Feature works but has issues
- Low: Minor cosmetic or edge case issues

---

## Notes and Observations

(Add any additional observations, suggestions, or feedback here)


---

## Sign-off

**Tested by:** _______________

**Date:** _______________

**Status:** ☐ All tests passed ☐ Issues found (see above) ☐ Re-test required
