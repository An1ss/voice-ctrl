# Voice Control - Installation and Testing Manual

**Version:** 1.0 (MVP Phase 1)
**Platform:** Ubuntu Linux with GNOME
**Date:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Testing Guide](#testing-guide)
5. [Troubleshooting](#troubleshooting)
6. [Usage Tips](#usage-tips)

---

## Overview

Voice Control is a system-wide voice dictation tool for Ubuntu that allows you to transcribe speech to text in any application using OpenAI's Whisper API.

**Key Features:**
- Global keyboard shortcut (Ctrl+Shift+Space)
- Real-time transcription using OpenAI Whisper API
- Automatic text insertion at cursor position
- System tray icon with status indicators
- Desktop notifications for errors
- Works in all applications: terminal, browser, text editors, etc.

**What Ralph Built:**
- ✅ Project structure with virtual environment
- ✅ Audio recording with keyboard shortcut
- ✅ OpenAI Whisper API integration
- ✅ Auto-paste functionality
- ✅ System tray icon
- ✅ Error handling with notifications

---

## Installation

### Prerequisites

- Ubuntu 20.04 or later (GNOME desktop environment)
- Python 3.8 or higher
- Internet connection
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Sudo/administrator access for system dependencies

### Step 1: Verify Python Version

```bash
python3 --version
```

**Expected output:** Python 3.8.x or higher (Ralph confirmed 3.12.3 works)

If Python is not installed or version is too old:
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

### Step 2: Navigate to Project Directory

```bash
cd /home/aniss/dev/voice-ctrl
```

### Step 3: Install System Dependencies

These are required for audio recording and clipboard access:

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev xclip
```

**What these do:**
- `portaudio19-dev` - Required by sounddevice library for audio recording
- `xclip` - Required by pyperclip for clipboard access on X11

### Step 4: Activate Virtual Environment

The virtual environment was already created by Ralph:

```bash
source venv/bin/activate
```

**Expected:** Your terminal prompt should change to show `(venv)` at the beginning.

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**This installs:**
- openai - OpenAI Whisper API client
- pynput - Global keyboard shortcuts
- sounddevice - Audio recording
- pystray - System tray icon
- pyperclip - Clipboard operations
- plyer - Desktop notifications
- pillow - Image processing for icons
- numpy - Audio data processing
- scipy - Audio file I/O

**Installation time:** ~2-3 minutes depending on internet speed

**Expected output:** Should end with "Successfully installed..." listing all packages

---

## Configuration

### Step 1: Create Configuration Directory

```bash
mkdir -p ~/.config/voice-ctrl
```

### Step 2: Create Configuration File

```bash
nano ~/.config/voice-ctrl/config.json
```

Or use any text editor you prefer.

### Step 3: Add Your OpenAI API Key

Paste the following into the config file:

```json
{
  "openai_api_key": "sk-YOUR-ACTUAL-API-KEY-HERE"
}
```

**Replace** `sk-YOUR-ACTUAL-API-KEY-HERE` with your actual OpenAI API key.

**To get an API key:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with "sk-")
5. Paste it into the config file

**Save and exit:**
- In nano: Press `Ctrl+X`, then `Y`, then `Enter`
- In vim: Press `Esc`, type `:wq`, press `Enter`

### Step 4: Verify Configuration

```bash
cat ~/.config/voice-ctrl/config.json
```

**Expected output:**
```json
{
  "openai_api_key": "sk-proj-..."
}
```

**Important:** Keep this API key private! Do not share or commit it to git.

---

## Testing Guide

### Quick Start Test (5 minutes)

This is the fastest way to verify everything works:

#### 1. Start the Application

```bash
cd /home/aniss/dev/voice-ctrl
source venv/bin/activate
python -m src.main
```

**Expected output:**
```
Voice Control is running. Press Ctrl+Shift+Space to record.
```

**What to check:**
- ✅ No error messages
- ✅ Application stays running (doesn't exit)
- ✅ System tray icon appears (look for microphone icon in your system tray)

#### 2. Open a Text Editor

In a new terminal window:

```bash
gedit &
```

Or use any text editor: VS Code, nano, LibreOffice Writer, etc.

#### 3. Test Recording

1. **Click in the text editor** to focus it
2. **Press Ctrl+Shift+Space** (starts recording)
   - System tray icon should turn RED
3. **Speak clearly:** "This is a test of the voice control system"
4. **Press Ctrl+Shift+Space** again (stops recording)
   - System tray icon should turn GRAY
5. **Wait 2-5 seconds** for transcription
6. **Text should appear** in your text editor

**Success criteria:**
- ✅ Text appears: "This is a test of the voice control system." (or similar)
- ✅ Icon changed from gray → red → gray
- ✅ No error notifications

**If it fails:**
- Check that your microphone is working
- Verify API key is correct
- Look for error notifications
- Check logs: `cat ~/.config/voice-ctrl/voice-ctrl.log`

---

### Comprehensive Testing

For thorough validation, complete these tests:

### Test 1: Application Startup

**Objective:** Verify the application starts correctly

**Steps:**
1. Open terminal
2. Run:
   ```bash
   cd /home/aniss/dev/voice-ctrl
   source venv/bin/activate
   python -m src.main
   ```

**Expected results:**
- ✅ Console shows: "Voice Control is running. Press Ctrl+Shift+Space to record."
- ✅ No Python errors or tracebacks
- ✅ System tray icon visible
- ✅ Tooltip shows "Voice Control" when hovering over icon

**Status:** Pass / Fail

---

### Test 2: Basic Recording

**Objective:** Verify audio recording works

**Steps:**
1. With application running, press **Ctrl+Shift+Space**
2. Speak for 5 seconds: "Testing one two three"
3. Press **Ctrl+Shift+Space** again

**Expected results:**
- ✅ Icon turns red during recording
- ✅ Icon returns to gray after stopping
- ✅ WAV file created in /tmp/ (verify with: `ls -ltr /tmp/*.wav | tail -1`)

**Verify audio format:**
```bash
file $(ls -t /tmp/*.wav | head -1)
```

**Should show:** WAVE audio, Microsoft PCM, 16 bit, mono 16000 Hz

**Status:** Pass / Fail

---

### Test 3: Transcription Accuracy

**Objective:** Verify OpenAI Whisper API integration

**Steps:**
1. Open text editor (gedit, VS Code, etc.)
2. Click in text area to focus
3. Press Ctrl+Shift+Space
4. Speak clearly: "Hello world, this is a voice to text test"
5. Press Ctrl+Shift+Space

**Expected results:**
- ✅ Text appears within 5 seconds
- ✅ Transcription accuracy ≥90% for clear speech
- ✅ Text inserted at cursor position
- ✅ Previous clipboard contents restored after paste

**Transcription:**
_______________________________________
(Write what appeared in the text editor)

**Accuracy:** Good / Fair / Poor

**Status:** Pass / Fail

---

### Test 4: Cross-Application Compatibility

**Objective:** Verify it works in different applications

Test in each of the following:

**4a. Terminal**
```bash
gnome-terminal
# In the terminal, press Ctrl+Shift+Space and speak
```
**Status:** Pass / Fail

**4b. Web Browser**
- Open Firefox or Chrome
- Navigate to any text field (e.g., Google search)
- Press Ctrl+Shift+Space and speak

**Status:** Pass / Fail

**4c. Text Editor (gedit)**
**Status:** Pass / Fail

**4d. VS Code (if installed)**
**Status:** Pass / Fail / N/A

---

### Test 5: Maximum Duration (240 seconds)

**Objective:** Verify auto-stop after 4 minutes

**Steps:**
1. Press Ctrl+Shift+Space
2. Leave microphone open or speak continuously
3. Wait for automatic stop

**Expected results:**
- ✅ Recording stops automatically at exactly 240 seconds
- ✅ Icon returns to gray
- ✅ No crash or freeze

**Actual duration:** _______ seconds

**Status:** Pass / Fail

---

### Test 6: Error Handling - No Audio

**Objective:** Verify error notification when no audio detected

**Steps:**
1. Mute your microphone OR unplug it
2. Press Ctrl+Shift+Space
3. Immediately press Ctrl+Shift+Space again (no speech)

**Expected results:**
- ✅ Desktop notification: "No audio detected. Please check your microphone."
- ✅ Error logged to ~/.config/voice-ctrl/voice-ctrl.log
- ✅ Application continues running (doesn't crash)

**Verify log:**
```bash
cat ~/.config/voice-ctrl/voice-ctrl.log
```

**Status:** Pass / Fail

---

### Test 7: Error Handling - Invalid API Key

**Objective:** Verify error handling for authentication failures

**Steps:**
1. Edit config file:
   ```bash
   nano ~/.config/voice-ctrl/config.json
   ```
2. Change API key to: `"sk-invalid-test-key"`
3. Save and exit
4. Restart application
5. Try recording

**Expected results:**
- ✅ Desktop notification: "Invalid API key. Check ~/.config/voice-ctrl/config.json"
- ✅ Error logged with details
- ✅ Application continues running

**Restore config:**
```bash
# Put your real API key back!
nano ~/.config/voice-ctrl/config.json
```

**Status:** Pass / Fail

---

### Test 8: System Tray Icon States

**Objective:** Verify icon state changes

**Steps:**
1. Start application → observe idle icon (gray)
2. Start recording → observe recording icon (red)
3. Stop recording → observe return to idle (gray)
4. Hover over icon → check tooltip

**Expected results:**
- ✅ Idle state: Gray microphone icon
- ✅ Recording state: Red microphone icon
- ✅ Real-time state updates
- ✅ Tooltip: "Voice Control"

**Status:** Pass / Fail

---

### Test 9: Desktop Notifications

**Objective:** Verify notification system works

**Error types to trigger:**
- Invalid API key (Test 7)
- No audio detected (Test 6)
- Missing config file (rename config.json temporarily)

**Expected results:**
- ✅ Notifications appear in system notification area
- ✅ Messages are user-friendly (not technical jargon)
- ✅ Notifications auto-dismiss after 5 seconds
- ✅ Can display multiple notifications

**Status:** Pass / Fail

---

### Test 10: Application Exit

**Objective:** Verify clean shutdown

**Steps:**
1. With application running, press **Ctrl+C** in terminal

**Expected results:**
- ✅ Application exits without errors
- ✅ System tray icon disappears
- ✅ No Python tracebacks
- ✅ No zombie processes (check with: `ps aux | grep main`)

**Status:** Pass / Fail

---

### Test 11: Rapid Toggle

**Objective:** Verify no race conditions or crashes

**Steps:**
1. Quickly press Ctrl+Shift+Space multiple times:
   - Press (start)
   - Wait 1 second
   - Press (stop)
   - Immediately press (start again)
   - Press (stop)

**Expected results:**
- ✅ No crashes
- ✅ Each recording creates a separate file
- ✅ State tracking remains accurate

**Status:** Pass / Fail

---

### Test 12: Long Transcription

**Objective:** Verify handling of long speech

**Steps:**
1. Speak continuously for 30-60 seconds
2. Verify transcription

**Expected results:**
- ✅ Long text pastes correctly
- ✅ No truncation
- ✅ Clipboard handles large text

**Status:** Pass / Fail

---

### Test 13: Special Characters

**Objective:** Verify punctuation handling

**Steps:**
1. Speak: "Testing punctuation: comma, period. Question mark? Exclamation point!"

**Expected results:**
- ✅ Whisper API adds punctuation automatically
- ✅ Special characters paste correctly

**Transcription:**
_______________________________________

**Status:** Pass / Fail

---

## Test Summary Checklist

Mark each test as you complete it:

- [ ] Test 1: Application Startup
- [ ] Test 2: Basic Recording
- [ ] Test 3: Transcription Accuracy
- [ ] Test 4a: Terminal compatibility
- [ ] Test 4b: Web browser compatibility
- [ ] Test 4c: Text editor compatibility
- [ ] Test 5: Maximum duration (240s)
- [ ] Test 6: No audio error handling
- [ ] Test 7: Invalid API key handling
- [ ] Test 8: System tray icon states
- [ ] Test 9: Desktop notifications
- [ ] Test 10: Clean exit
- [ ] Test 11: Rapid toggle
- [ ] Test 12: Long transcription
- [ ] Test 13: Special characters

**Tests Passed:** _____ / 13

**Overall Status:** Pass / Fail

**Notes:**
_______________________________________
_______________________________________
_______________________________________

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'sounddevice'"

**Cause:** Python dependencies not installed

**Solution:**
```bash
cd /home/aniss/dev/voice-ctrl
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problem: "OSError: PortAudio library not found"

**Cause:** System dependency missing

**Solution:**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev
```

Then restart the application.

---

### Problem: "Pyperclip could not find a copy/paste mechanism"

**Cause:** Clipboard tool not installed

**Solution:**
```bash
sudo apt-get install xclip
```

For Wayland (instead of X11):
```bash
sudo apt-get install wl-clipboard
```

---

### Problem: System tray icon doesn't appear

**Cause:** Desktop environment doesn't support system tray or extension needed

**Solution for GNOME:**
```bash
# Install TopIcons Plus extension
gnome-extensions install topicons-plus@phocean.net
# Or use GNOME Extensions website: https://extensions.gnome.org/
```

**Alternative:** Check if your desktop environment supports system tray icons natively.

---

### Problem: "Invalid API key" notification appears

**Cause:** API key is incorrect or missing

**Solution:**

1. Verify config file exists:
   ```bash
   cat ~/.config/voice-ctrl/config.json
   ```

2. Check API key format (should start with "sk-"):
   ```json
   {
     "openai_api_key": "sk-proj-..."
   }
   ```

3. Get a new API key from: https://platform.openai.com/api-keys

4. Update config file:
   ```bash
   nano ~/.config/voice-ctrl/config.json
   ```

---

### Problem: No audio is recorded (silence)

**Possible causes and solutions:**

**1. Microphone is muted**
```bash
# Check microphone status
pactl list sources | grep -A 10 "analog-input-mic"
```

**2. Wrong microphone selected**
- Check Ubuntu Sound Settings
- Ensure correct input device is selected
- Test microphone with: `arecord -d 5 test.wav && aplay test.wav`

**3. Permission issues**
- Ensure user is in audio group:
  ```bash
  groups | grep audio
  ```
- If not, add yourself:
  ```bash
  sudo usermod -a -G audio $USER
  # Then log out and log back in
  ```

---

### Problem: Transcription is inaccurate

**Possible causes:**

**1. Background noise**
- Use in quiet environment
- Speak clearly and directly into microphone
- Check microphone quality

**2. Speaking too fast/slow**
- Speak at normal conversational pace
- Pause briefly between sentences

**3. Technical/domain-specific terms**
- Whisper may not recognize specialized jargon
- Spell out acronyms when speaking

---

### Problem: Application crashes or freezes

**Steps to diagnose:**

1. **Check logs:**
   ```bash
   cat ~/.config/voice-ctrl/voice-ctrl.log
   ```

2. **Run with verbose output:**
   ```bash
   python -m src.main 2>&1 | tee debug.log
   ```

3. **Check for orphaned processes:**
   ```bash
   ps aux | grep python | grep main
   killall -9 python  # If needed to clean up
   ```

4. **Verify dependencies:**
   ```bash
   pip list | grep -E "openai|pynput|sounddevice|pystray|pyperclip|plyer"
   ```

---

### Problem: Shortcut (Ctrl+Shift+Space) doesn't work

**Possible causes:**

**1. Keyboard shortcut conflict**
- Another application is using the same shortcut
- Check Ubuntu keyboard shortcuts: Settings → Keyboard → View and Customize Shortcuts

**2. Permission issues**
- pynput may need additional permissions
- Try running with sudo (not recommended for production):
  ```bash
  sudo python -m src.main
  ```

**3. X11 vs Wayland**
- Global hotkeys work better on X11
- If using Wayland, try switching to X11 session

---

## Usage Tips

### Best Practices

1. **Speak clearly** - Use normal conversational pace
2. **Quiet environment** - Minimize background noise
3. **Good microphone** - Use quality microphone for better results
4. **Pause between thoughts** - Helps Whisper add punctuation
5. **Review transcription** - Always check for accuracy

### Common Commands

**Start application:**
```bash
cd /home/aniss/dev/voice-ctrl
source venv/bin/activate
python -m src.main
```

**Stop application:**
- Press `Ctrl+C` in terminal

**Check status:**
```bash
# View logs
cat ~/.config/voice-ctrl/voice-ctrl.log

# List recent recordings
ls -ltr /tmp/*.wav | tail -5

# Check if running
ps aux | grep main
```

**Update dependencies:**
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## Cost Information

**OpenAI Whisper API Pricing (as of January 2026):**
- $0.006 per minute of audio

**Example costs:**
- 10 seconds of speech: ~$0.001
- 1 minute: $0.006
- 10 minutes per day: $0.06/day = $1.80/month
- 100 transcriptions (avg 30s each): ~$0.30

**Monitor your usage at:** https://platform.openai.com/usage

---

## Known Limitations

These are expected limitations (not bugs):

- ✅ Requires internet connection (OpenAI API)
- ✅ English optimized (auto-detects other languages)
- ✅ 240 second (4 minute) maximum per recording
- ✅ No offline mode
- ✅ No recording playback/preview
- ✅ Costs money per transcription
- ✅ Ubuntu/Linux only (not Windows/macOS)

---

## Next Steps

### After Successful Testing

If all tests pass, you can:

1. **Set up auto-start** (systemd service)
2. **Create desktop entry** for easy launching
3. **Package as .deb** for distribution
4. **Implement Phase 2 features**:
   - Configuration UI
   - Audio feedback (beeps)
   - Configurable keyboard shortcut
   - Multiple language support

---

## Support

**Documentation:**
- README: `/home/aniss/dev/voice-ctrl/README.md`
- PRD: `/home/aniss/dev/voice-ctrl/tasks/prd-voice-dictation-app.md`
- Progress Log: `/home/aniss/dev/voice-ctrl/scripts/ralph/progress.txt`

**Logs:**
- Application logs: `~/.config/voice-ctrl/voice-ctrl.log`

**OpenAI Documentation:**
- Whisper API: https://platform.openai.com/docs/guides/speech-to-text
- API Keys: https://platform.openai.com/api-keys
- Usage & Billing: https://platform.openai.com/usage

---

## Version History

**1.0 - MVP Phase 1** (January 2026)
- Initial release with core functionality
- Built autonomously by Ralph AI
- 6 user stories implemented
- All tests passing

---

**End of Installation and Testing Manual**
