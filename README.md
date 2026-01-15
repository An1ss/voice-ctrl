# VoiceControl

System-wide voice dictation tool for Ubuntu using OpenAI Whisper API.

## Overview

VoiceControl is a voice-to-text application that enables hands-free typing across all applications on Ubuntu. Press a keyboard shortcut, speak, and your words are transcribed and inserted at your cursor position.

## Features

- Configurable global keyboard shortcut for voice recording (default: Ctrl+Shift+Space)
- Real-time transcription using OpenAI Whisper API
- Automatic text insertion at cursor position
- System tray icon with status indicators
- Desktop notifications for errors and important events
- Works across all applications: terminal, browser, text editors, IDEs
- Transcription history (last 30 entries)
- .deb package for easy installation
- Autostart support (Start at Login)

## Future Features

Planned improvements and features under consideration:

### High Priority

- **Local Processing Support**: Integrate whisper.cpp for completely offline transcription (privacy-first, no data leaves your device)
- **Multiple Voice Provider Options**: Add support for alternative transcription APIs:
  - [Groq](https://groq.com/) (Whisper Large v3 Turbo - ultra-fast, low cost)
  - [Deepgram Nova-3](https://deepgram.com/) (sub-300ms latency, high accuracy)
  - [AssemblyAI Universal-2](https://www.assemblyai.com/) (99+ languages, sentiment analysis, speaker diarization)
  - [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text) (Chirp - 125+ languages)
  - Local models via [Voxtral](https://mistral.ai/) (Mistral AI's open-source alternative)

### Medium Priority

- **SQLite Database**: Migrate from JSON to SQLite for more robust history storage
  - Remove 30-entry limit
  - Better query performance
  - Search and filter capabilities
- **AppImage Packaging**: Universal Linux package that works on all distributions without installation
- **Additional Package Formats**: .rpm (Fedora/RHEL), flatpak (sandboxed), tar.gz (universal archive)

### Lower Priority

- **Enhanced Visual Feedback**: Recording/processing animations in tray icon
- **Improved History UI**: Better layout, timestamps, copy buttons, search functionality
- **Model Management UI**: If local processing is added, allow users to download and manage different Whisper models

See [COMPETITOR_ANALYSIS.md](docs/COMPETITOR_ANALYSIS.md) for detailed research on these features.

## Requirements

- Python 3.8 or higher
- Ubuntu (GNOME desktop environment)
- OpenAI API key
- System dependencies:
  - `portaudio19-dev` (for audio recording)
  - `xclip` (for clipboard access)
  - `python3-tk` (for settings GUI)
  - `python3-gi`, `python3-gi-cairo`, `gir1.2-gtk-3.0` (for system tray icon with AppIndicator)

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd voice-ctrl
```

### 2. Install system dependencies

**Important:** Install system dependencies before creating the virtual environment.

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev xclip python3-tk python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### 3. Create virtual environment

```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

**Note:** The `--system-site-packages` flag is required to access the system-installed PyGObject libraries needed for the system tray icon.

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m src.main
```

On first launch, a setup wizard will guide you through configuring your OpenAI API key.

Alternatively, you can manually create the configuration file at `~/.config/voice-ctrl/config.json`:

```json
{
  "api_key": "your-openai-api-key-here",
  "max_duration_seconds": 240,
  "audio_feedback_enabled": true,
  "keyboard_shortcut": "Ctrl+Shift+Space"
}
```

**Configuration Options:**

- `api_key` (string): Your OpenAI API key (required for transcription)
- `max_duration_seconds` (number): Maximum recording duration in seconds (default: 240)
- `audio_feedback_enabled` (boolean): Enable audio beeps for recording feedback (default: true)
- `keyboard_shortcut` (string): Keyboard shortcut for recording (default: "Ctrl+Shift+Space")
  - Valid formats: "Ctrl+Shift+Space", "Alt+F1", "Ctrl+Alt+R", "Shift+Insert"
  - Requires at least one modifier key (Ctrl, Alt, Shift) plus another key
  - Changing this setting requires restarting the application

## Usage

1. Start the application
2. Look for the system tray icon (microphone)
3. Press your configured keyboard shortcut (default: **Ctrl+Shift+Space**) to start recording
4. Speak your text
5. Press the shortcut again to stop and transcribe
6. The text will be automatically inserted at your cursor position

### System Tray Menu

Right-click the tray icon to access:
- **Settings**: Open the settings window to configure all options with a GUI
- **About**: View application information
- **Quit**: Exit the application

### Settings Window

The settings window allows you to configure:
- OpenAI API Key
- Maximum recording duration
- Audio feedback (beeps)
- Keyboard shortcut

Changes are saved immediately to the config file. Note that keyboard shortcut changes require restarting the application.

**Note:** If the keyboard shortcut conflicts with another application, you can change it in the Settings window or manually edit `~/.config/voice-ctrl/config.json` and restart the application.

## Project Structure

```
voice-ctrl/
├── src/                  # Source code
├── config/              # Configuration files
├── tests/               # Unit tests
├── scripts/ralph/       # Development automation scripts
├── venv/                # Virtual environment (git-ignored)
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Development

Activate the virtual environment before development:

```bash
source venv/bin/activate
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'sounddevice'"

**Cause:** Python dependencies not installed

**Solution:**
```bash
cd /path/to/voice-ctrl
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
# Install AppIndicator extension from GNOME Extensions website
# https://extensions.gnome.org/extension/615/appindicator-support/
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
     "api_key": "sk-proj-..."
   }
   ```

3. Get a new API key from: https://platform.openai.com/api-keys

4. Update config file through Settings window or manually edit:
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
- Change shortcut in VoiceControl Settings window

**2. Permission issues**
- pynput may need additional permissions on some systems

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

### Cost Information

**OpenAI Whisper API Pricing:**
- $0.006 per minute of audio

**Example costs:**
- 10 seconds of speech: ~$0.001
- 1 minute: $0.006
- 10 minutes per day: $0.06/day = $1.80/month
- 100 transcriptions (avg 30s each): ~$0.30

**Monitor your usage at:** https://platform.openai.com/usage

---

## License

TBD
