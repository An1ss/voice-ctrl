# VoiceControl Testing Plan

Quick testing checklist for verifying Ralph's implementation.

---

## US-005: System Tray Icon - Hover Tooltip

**Test:**
1. Start app: `python -m src.main`
2. Hover mouse over tray icon
3. Should see tooltip: "Voice Control"

**Expected:** ✓ Tooltip appears
**Result:** Fail
**Notes:** Nothing appears on hover

---

## US-006: Error Notifications

**Test:**
1. Edit config: `nano ~/.config/voice-ctrl/config.json`
2. Set invalid API key: `"api_key": "sk-invalid-test"`
3. Save and restart app
4. Trigger recording (say something)
5. Should see desktop notification with error message

**Expected:** ✓ Desktop notification shows "Invalid API key" or similar
**Result:** Pass

**Cleanup:** Restore valid API key in config file!

---

## US-008: Config File - All Parameters

**Test:**
1. Check current config: `cat ~/.config/voice-ctrl/config.json`
2. Should have all these settings:
   - `api_key`
   - `max_duration_seconds`
   - `audio_feedback_enabled`
   - `keyboard_shortcut`

**Current config has:** It had only the api by default, but I changed it manually. Is it supposed to be initialized automatically? 

**Test changing max_duration:**
1. Edit config: set `"max_duration_seconds": 10`
2. Restart app
3. Start recording and wait 10+ seconds
4. Should auto-stop at 10 seconds

**Expected:** ✓ Auto-stops at configured time
**Result:** Partial fail : It did stop after 10 seconds but the problem is that the recording was not transcribed so it just kind of exits after 10 seconds. what we want is that it stops at 10 seconds but it does send the recording to transcription

**Cleanup:** Restore `"max_duration_seconds": 240`

---

## US-009: Audio Feedback (Beeps)

**Already confirmed working by user** ✓

---

## US-010: Configurable Keyboard Shortcut

**Test:**
1. Edit config: `nano ~/.config/voice-ctrl/config.json`
2. Change to: `"keyboard_shortcut": "Ctrl+Alt+R"`
3. Save and restart app
4. Try **Ctrl+Alt+R** - should trigger recording
5. Try old shortcut **Ctrl+Shift+Space** - should NOT work

**Expected:** ✓ New shortcut works, old doesn't
**Result:** Pass

**Cleanup:** Change back to `"keyboard_shortcut": "Ctrl+Shift+Space"`

---

## US-011: Settings Window from Tray Icon

**Known Issue:** User reports right-click on tray icon does nothing

**Test:**
1. Right-click tray icon
2. Should see menu with: Settings, About, Quit

**Expected:** ✓ Menu appears with 3 options
**Actual:** Menu does NOT appear
**Result:** **FAIL** - Needs fixing

**If menu works, test Settings window:**
1. Click "Settings"
2. Window should open with editable fields:
   - API Key
   - Max Duration
   - Audio Feedback checkbox
   - Keyboard Shortcut
3. Make a change and save
4. Verify change in `~/.config/voice-ctrl/config.json`

---

## US-012: API Key Setup Wizard

**Test (requires backup first):**

**Backup config:**
```bash
mv ~/.config/voice-ctrl/config.json ~/.config/voice-ctrl/config.json.backup
```

**Test:**
1. Start app (with no config file)
2. Setup wizard should appear automatically
3. Should have:
   - Field to enter API key
   - "Get API Key" button (opens browser)
   - Validate & Save button
4. Try entering invalid key: `sk-test`
5. Should show error
6. Try entering valid key
7. Should save to config file

**Expected:** ✓ Wizard appears and works
**Result:** Fail : Almost a pass, everything works great but the save button is not visible. I was able to save by hitting enter though

**Restore config:**
```bash
mv ~/.config/voice-ctrl/config.json.backup ~/.config/voice-ctrl/config.json
```



## Additional issue - xclip timeout warnings

Noticed this in the app terminal, everything was working fine though...

```bash
System tray icon started
Recording started... (max 240s)
Tray icon state: recording
Recording stopped. Duration: 4.63s
Audio saved to: /tmp/voice_recording_20260113_105453.wav
Tray icon state: idle
Processing audio...
Transcribing audio file: /tmp/voice_recording_20260113_105453.wav
Transcription successful: Hello, this is a test, test in, test in, 1, 2, 3.
Cleaned up temporary audio file: /tmp/voice_recording_20260113_105453.wav
Pasting transcribed text...
WARNING: Failed to copy to CLIPBOARD via xclip: Command '['xclip', '-selection', 'clipboard']' timed out after 1.0 seconds
WARNING: Failed to copy to PRIMARY selection: Command '['xclip', '-selection', 'primary']' timed out after 1.0 seconds
Simulated Shift+Insert keystroke
Restored previous clipboard contents
```

**Status:** Identified as US-018 - xclip timeout too short (1.0s)

---

## Fixes Applied During Testing

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

## Summary

**Tests Completed:** 6 / 6
**Passing:** 3 (US-006, US-009, US-010)
**Failing:** 3 (US-005, US-008, US-011, US-012, US-015)
**Fixed During Testing:** 2 (US-012.1, tray icon crash)

**Remaining Issues for Ralph (US-013 to US-018):**
- US-013: Tray icon tooltip not showing on hover
- US-014: Config file missing default parameters
- US-015: Auto-stop doesn't transcribe recording
- US-016: Right-click menu on tray icon not working
- US-017: Setup wizard save button not visible
- US-018: xclip timeout warnings (1.0s too short)

**Action Items:**
- [x] Fix terminal paste issue (US-012.1) - DONE
- [x] Fix tray icon startup crash - DONE
- [ ] Run Ralph to fix remaining 6 bugs (US-013 to US-018)
