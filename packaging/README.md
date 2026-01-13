# VoiceControl Debian Package

This directory contains the structure for building the VoiceControl .deb package.

## Package Structure

```
voice-ctrl/
├── DEBIAN/
│   ├── control         # Package metadata and dependencies
│   ├── postinst        # Post-installation script (sets up venv)
│   └── prerm           # Pre-removal script (cleanup)
├── opt/voice-ctrl/     # Application files (populated during build)
│   ├── src/
│   ├── requirements.txt
│   └── README.md
├── usr/bin/
│   └── voice-ctrl      # Launcher script
├── usr/share/applications/
│   └── voice-ctrl.desktop  # Desktop entry for app menu
└── usr/share/pixmaps/
    └── voice-ctrl.png  # Application icon
```

## Building the Package

Run the build script from the project root:

```bash
./build_deb.sh
```

This will create `voice-ctrl.deb` in the project root.

## Installation

```bash
sudo dpkg -i voice-ctrl.deb
sudo apt-get install -f  # Install dependencies if needed
```

## Uninstallation

```bash
sudo apt remove voice-ctrl
```

## Dependencies

The package depends on:
- python3 (>= 3.8)
- python3-venv
- portaudio19-dev
- xclip
- python3-tk
- python3-gi
- python3-gi-cairo
- gir1.2-gtk-3.0

Python dependencies (installed via pip in postinst):
- openai
- pynput
- sounddevice
- numpy
- pystray
- pyperclip
- plyer

## How It Works

1. **Installation**: `dpkg -i` extracts files to their locations
2. **Post-install** (`postinst`): Creates virtual environment and installs Python dependencies
3. **Launcher**: `/usr/bin/voice-ctrl` activates venv and runs the application
4. **Desktop Entry**: `.desktop` file allows launching from application menu
5. **Uninstall** (`prerm`): Removes autostart file if present
