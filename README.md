# VoiceControl

System-wide voice dictation tool for Ubuntu using OpenAI Whisper API.

## Overview

VoiceControl is a voice-to-text application that enables hands-free typing across all applications on Ubuntu. Press a keyboard shortcut, speak, and your words are transcribed and inserted at your cursor position.

## Features

- Global keyboard shortcut for voice recording (Ctrl+Shift+Space)
- Real-time transcription using OpenAI Whisper API
- Automatic text insertion at cursor position
- System tray icon with status indicators
- Desktop notifications for errors and important events
- Works across all applications: terminal, browser, text editors, IDEs

## Requirements

- Python 3.8 or higher
- Ubuntu (GNOME desktop environment)
- OpenAI API key

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

Create a configuration file at `~/.config/voice-ctrl/config.json`:

```bash
mkdir -p ~/.config/voice-ctrl
```

Add your OpenAI API key to the config file:

```json
{
  "api_key": "your-openai-api-key-here"
}
```

### 5. Run the application

```bash
python -m src.main
```

## Usage

1. Start the application
2. Look for the system tray icon (microphone)
3. Press **Ctrl+Shift+Space** to start recording
4. Speak your text
5. Press **Ctrl+Shift+Space** again to stop and transcribe
6. The text will be automatically inserted at your cursor position

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
