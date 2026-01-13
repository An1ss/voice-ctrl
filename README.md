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

## Requirements

- Python 3.8 or higher
- Ubuntu (GNOME desktop environment)
- OpenAI API key
- System dependencies: `portaudio19-dev` (for audio recording), `xclip` (for clipboard access), `python3-tk` (for settings GUI)

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd voice-ctrl
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install system dependencies

```bash
sudo apt-get update
sudo apt-get install portaudio19-dev xclip python3-tk
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API key

A configuration file will be automatically created at `~/.config/voice-ctrl/config.json` when you first run the application. You can manually create it beforehand:

```bash
mkdir -p ~/.config/voice-ctrl
```

Edit the configuration file with your settings:

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

### 6. Run the application

```bash
python -m src.main
```

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

## License

TBD
