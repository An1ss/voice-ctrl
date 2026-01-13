# VoiceControl Testing Plan - Round 2

Re-testing after Ralph's bug fixes (US-013 to US-018).

---

## Fixes Applied During Round 1 Testing

### US-012.1: Terminal Paste Issue (FIXED ✓)
**Issue:** Shift+Insert in terminals was pasting old clipboard content
**Root Cause:** Linux X11 has separate CLIPBOARD and PRIMARY selections. pyperclip only wrote to CLIPBOARD, but Shift+Insert reads from PRIMARY
**Fix:** Updated src/paster.py to copy to both CLIPBOARD and PRIMARY selections using xclip
**Status:** Fixed and committed

### Tray Icon Menu Crash (FIXED ✓)
**Issue:** App crashed on startup with "TypeError: pystray._base.Menu() argument after * must be an iterable, not function"
**Root Cause:** _create_menu() returned raw function instead of Menu object
**Fix:** Wrapped menu_builder with Menu() in src/tray_icon.py
**Status:** Fixed and committed

---

## Re-Testing After Ralph's Fixes

Ralph has attempted to fix US-013 through US-018. Test each fix:

### US-013: Tray Icon Tooltip
**Test:**
1. Start app: `python -m src.main`
2. Hover mouse over tray icon
3. Should see tooltip: "Voice Control"

**Expected:** ✓ Tooltip appears within 1 second
**Result:** Passed
**Notes:**

---

### US-014: Config Auto-Initialization
**Test:**

1. Backup current config: `mv ~/.config/voice-ctrl/config.json ~/.config/voice-ctrl/config.json.bak`
2. Start app (will trigger setup wizard or create new config)
3. After setup, check config: `cat ~/.config/voice-ctrl/config.json`
4. Should have ALL parameters:
   - `api_key`
   - `max_duration_seconds` (240)
   - `audio_feedback_enabled` (true)
   - `keyboard_shortcut` ("Ctrl+Shift+Space")

**Expected:** ✓ All 4 parameters present with defaults
**Result:**
**Notes:**

**Cleanup:** `mv ~/.config/voice-ctrl/config.json.bak ~/.config/voice-ctrl/config.json`

---

### US-015: Auto-Stop Transcription
**Test:**

1. Edit config: `nano ~/.config/voice-ctrl/config.json`
2. Set `"max_duration_seconds": 10`
3. Restart app
4. Open text editor
5. Start recording and keep talking for 15+ seconds
6. Should auto-stop at 10 seconds AND transcribe

**Expected:** ✓ Recording stops at 10s AND text is transcribed and pasted
**Result:** Pass
**Notes:**

**Cleanup:** Restore `"max_duration_seconds": 240`

---

### US-016: Tray Icon Right-Click Menu
**Test:**
1. Start app
2. Right-click tray icon
3. Should see menu with: Settings, About, Quit

**Expected:** ✓ Menu appears with 3 items
**Result:** Pass

**If menu appears, test each item:**
- [ ] "Settings" opens settings window
- [ ] "About" shows about dialog
- [ ] "Quit" exits application cleanly

**Notes:**

---

### US-017: Setup Wizard Save Button
**Test:**
1. Backup config: `mv ~/.config/voice-ctrl/config.json ~/.config/voice-ctrl/config.json.bak`
2. Start app (wizard should appear)
3. Check if "Validate & Save" button is VISIBLE
4. Click the button (don't use Enter)
5. Button should save the config

**Expected:** ✓ Button is visible and clickable
**Result:** Pass
**Notes:**

**Cleanup:** `mv ~/.config/voice-ctrl/config.json.bak ~/.config/voice-ctrl/config.json`

---

### US-018: xclip Timeout Warnings
**Test:**
1. Start app
2. Trigger recording 3-5 times
3. Watch console output during paste
4. Should NOT see timeout warnings

**Expected:** ✓ No warnings like "Failed to copy to CLIPBOARD via xclip: timeout"
**Result:** Pass
**Console output:**

---

## Re-Test Summary

After testing, fill in:

**Tests Passing:** ___ / 6
**Tests Failing:** ___ / 6

**Bugs Fixed by Ralph:**
- [ ] US-013: Tray tooltip
- [ ] US-014: Config initialization
- [ ] US-015: Auto-stop transcription
- [ ] US-016: Right-click menu
- [ ] US-017: Save button visibility
- [ ] US-018: xclip timeout

**Any New Issues Found:**
