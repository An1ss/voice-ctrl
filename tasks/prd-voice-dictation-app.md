# PRD: Voice Control - System-Wide Dictation App for Ubuntu

## Introduction

A system-wide dictation tool for Ubuntu that allows users to transcribe speech to text from any application. Users trigger recording with a keyboard shortcut (Ctrl+Shift+Space), speak into their microphone, press the shortcut again to stop, and the transcribed text is automatically inserted at the cursor position. The app uses OpenAI's Whisper API for high-quality transcription and runs persistently with a system tray icon for visual feedback.

## Goals

- Enable hands-free text input in any Ubuntu application
- Provide instant, accurate transcription using OpenAI Whisper API
- Minimize friction with simple keyboard shortcut activation
- Give clear visual and audio feedback during recording
- Allow user customization through configuration file
- Build incrementally with phased rollout

## User Stories

### Phase 1: MVP - Core Functionality

#### US-001: Set up project structure
**Description:** As a developer, I need a proper project structure so development is organized and maintainable.

**Acceptance Criteria:**
- [ ] Python project created with virtual environment
- [ ] Directory structure: `src/`, `config/`, `tests/`, `README.md`
- [ ] Dependencies file (`requirements.txt` or `pyproject.toml`)
- [ ] `.gitignore` configured for Python projects
- [ ] Basic README with setup instructions

#### US-002: Record audio on keyboard shortcut
**Description:** As a user, I want to press Ctrl+Shift+Space to start recording my voice so I can dictate text.

**Acceptance Criteria:**
- [ ] Global keyboard shortcut listener registers Ctrl+Shift+Space
- [ ] Pressing shortcut starts audio recording from default microphone
- [ ] Recording continues until shortcut is pressed again
- [ ] Audio is captured in format compatible with OpenAI Whisper API (e.g., WAV, MP3)
- [ ] Maximum recording duration hardcoded to 240 seconds (4 minutes) in MVP
- [ ] Recording stops automatically if max duration reached

#### US-003: Transcribe audio using OpenAI Whisper API
**Description:** As a user, I want my recorded speech automatically transcribed so I can get text without typing.

**Acceptance Criteria:**
- [ ] Audio file sent to OpenAI Whisper API (`/v1/audio/transcriptions` endpoint)
- [ ] API key read from config file at `~/.config/voice-ctrl/config.json`
- [ ] Successful transcription returns text string
- [ ] Handles API errors gracefully (network issues, invalid API key, etc.)
- [ ] Temporary audio file cleaned up after transcription

#### US-004: Insert transcribed text automatically
**Description:** As a user, I want the transcribed text automatically pasted at my cursor position so I can continue working without interruption.

**Acceptance Criteria:**
- [ ] Transcribed text copied to system clipboard
- [ ] Ctrl+V keystroke simulated to paste text
- [ ] Works in any application (terminal, browser, text editor, etc.)
- [ ] Clipboard restored to previous contents after paste (optional but nice)
- [ ] Focus returns to original application window

#### US-005: Show system tray icon
**Description:** As a user, I want a system tray icon so I know the app is running and can see recording status.

**Acceptance Criteria:**
- [ ] Icon appears in system tray when app starts
- [ ] Default state shows idle icon (microphone off)
- [ ] Recording state shows different icon (microphone on/red indicator)
- [ ] Icon visible in Ubuntu system tray (GNOME Shell, Unity, or compatible)
- [ ] Tooltip shows "Voice Control" when hovering

#### US-006: Handle errors with notifications
**Description:** As a user, I want to see error messages if something goes wrong so I understand what happened.

**Acceptance Criteria:**
- [ ] Desktop notification shown for errors (e.g., "Transcription failed: API error")
- [ ] Specific error messages for: no audio detected, API failure, network timeout, invalid API key
- [ ] Errors logged to file at `~/.config/voice-ctrl/voice-ctrl.log`
- [ ] App remains running after non-fatal errors

### Phase 1.5: Terminal Compatibility Fix

#### US-007: Use Shift+Insert for pasting instead of Ctrl+V
**Description:** As a user, I want text to paste using Shift+Insert so it works properly in command-line tools and terminals.

**Acceptance Criteria:**
- [ ] Shift+Insert keystroke simulated instead of Ctrl+V
- [ ] Text pastes successfully in terminal applications: bash, zsh, gnome-terminal
- [ ] Text pastes successfully in terminal editors: vim, nano, emacs
- [ ] Text pastes successfully in GUI applications: Firefox, VS Code, gedit
- [ ] Works inside tmux and screen sessions
- [ ] No regression in paste functionality
- [ ] Manual test: Record speech and verify paste works in terminal, vim, and browser

**Technical Notes:**
- Shift+Insert is the standard paste shortcut in terminals and most Linux applications
- Ctrl+V may be intercepted by terminal emulators for other functions (e.g., in vim it's visual block mode)
- Both shortcuts work in most GUI applications, but Shift+Insert has better terminal support

### Phase 2: Configuration & Polish

#### US-008: Load settings from config file
**Description:** As a user, I want to customize app behavior through a config file so I can adjust it to my preferences.

**Acceptance Criteria:**
- [ ] Config file created at `~/.config/voice-ctrl/config.json` on first run
- [ ] Default config includes: `api_key`, `max_duration_seconds`, `audio_feedback_enabled`
- [ ] Settings loaded at startup and applied
- [ ] Invalid config shows error notification with details
- [ ] Example config file documented in README

**Example config.json:**
```json
{
  "openai_api_key": "sk-...",
  "max_duration_seconds": 240,
  "audio_feedback_enabled": true,
  "keyboard_shortcut": "Ctrl+Shift+Space"
}
```

#### US-009: Add audio feedback (beeps)
**Description:** As a user, I want to hear beeps when recording starts/stops so I have confirmation without looking at the screen.

**Acceptance Criteria:**
- [ ] Play start beep when recording begins
- [ ] Play stop beep when recording ends
- [ ] Audio feedback respects `audio_feedback_enabled` config setting
- [ ] Beeps are short, non-intrusive system sounds
- [ ] Works even if system volume is low (reasonable volume)

#### US-010: Make keyboard shortcut configurable
**Description:** As a user, I want to change the keyboard shortcut so it doesn't conflict with other apps.

**Acceptance Criteria:**
- [ ] `keyboard_shortcut` setting in config file (e.g., "Ctrl+Shift+Space")
- [ ] App parses shortcut string and registers it on startup
- [ ] Invalid shortcut shows error with valid format examples
- [ ] Changing config requires app restart (document this limitation)

### Phase 3: GUI Settings (Future)

#### US-011: Add settings window from tray icon
**Description:** As a user, I want to click the tray icon and open a settings window so I can adjust preferences without editing JSON.

**Acceptance Criteria:**
- [ ] Right-click tray icon shows menu: "Settings", "About", "Quit"
- [ ] Settings window shows all configurable options with UI controls
- [ ] Changes saved to config file immediately
- [ ] Settings window has "Test Recording" button to verify setup
- [ ] Verify in browser using dev-browser skill (if web-based) OR manual verification

#### US-012: API key setup wizard
**Description:** As a new user, I want a guided setup on first launch so I can easily configure the app.

**Acceptance Criteria:**
- [ ] First launch detects missing/invalid API key
- [ ] Shows setup dialog requesting OpenAI API key
- [ ] "Get API Key" button opens https://platform.openai.com/api-keys
- [ ] Validates API key by making test request
- [ ] Saves valid key to config file

### Phase 4: Local Speech-to-Text (STT)

#### US-022: Add local STT config and defaults
**Description:** As a user, I want local STT settings saved in config so my choices persist across restarts.

**Acceptance Criteria:**
- [ ] Config file includes new fields: `stt_provider`, `local_engine`, `local_model_path`, `local_model_id`, `local_scan_paths`
- [ ] Defaults are set on first run and migrated into existing configs
- [ ] `stt_provider` supports `openai` and `local` values
- [ ] Invalid config values trigger a user notification and revert to defaults

#### US-023: Local STT engine wrapper (faster-whisper)
**Description:** As a user, I want transcription to run with faster-whisper so I can avoid API costs.

**Acceptance Criteria:**
- [ ] A new local transcriber uses faster-whisper for transcription from WAV input
- [ ] Engine supports model path and model ID (Hugging Face model name) inputs
- [ ] Transcription returns a plain text string or `None` on failure
- [ ] Errors are logged and surfaced via desktop notification
- [ ] OpenAI transcription path remains unchanged when `stt_provider` is `openai`

#### US-024: Model discovery by scanning folders
**Description:** As a user, I want the app to scan for existing local models so I can reuse downloads from other apps.

**Acceptance Criteria:**
- [ ] On demand, scan default paths (e.g., `~/.cache`, `~/.local/share`, `~/Downloads`)
- [ ] Allow scanning a user-selected folder
- [ ] Detected models are shown in Settings as selectable options
- [ ] Each detected model includes a label (model name) and path
- [ ] Scanning does not block the UI (runs in a background thread)
- [ ] Verify in browser using dev-browser skill

#### US-025: Settings UI for local STT selection
**Description:** As a user, I want to configure local STT in the Settings window so I can easily switch providers and models.

**Acceptance Criteria:**
- [ ] Settings includes a provider selector: `OpenAI` or `Local`
- [ ] When `Local` is selected, show engine selector (default: faster-whisper)
- [ ] Show model dropdown or radio list populated by scan results
- [ ] Provide buttons: "Scan Default Paths" and "Scan Folder..."
- [ ] Provide a field for `model_id` with a "Download Model" action
- [ ] Saving settings updates config immediately
- [ ] Verify in browser using dev-browser skill

#### US-026: Model download from scratch
**Description:** As a user, I want to download a local model by name so I can use local STT without manual setup.

**Acceptance Criteria:**
- [ ] Given a model ID (e.g., `openai/whisper-small`), the app downloads it to a local cache
- [ ] Progress or status is shown in Settings during download
- [ ] Downloaded model appears in the model selection list
- [ ] Errors (network, invalid model ID) show a notification
- [ ] Verify in browser using dev-browser skill

#### US-027: Fallback to OpenAI on local failure
**Description:** As a user, I want the app to fall back to OpenAI when local transcription fails so I can still get results.

**Acceptance Criteria:**
- [ ] If local transcription fails, notify the user with a concise error
- [ ] Automatically retry with OpenAI Whisper API
- [ ] If OpenAI also fails, show a single final error notification
- [ ] History logging still records the transcription when fallback succeeds

## Functional Requirements

**Core Functionality:**
- FR-1: The system must register a global keyboard shortcut (Ctrl+Shift+Space by default) that works across all applications
- FR-2: When the shortcut is pressed, the system must begin recording audio from the default microphone
- FR-3: When the shortcut is pressed again, the system must stop recording and save audio to temporary file
- FR-4: The system must send the audio file to OpenAI Whisper API and retrieve transcribed text
- FR-5: The system must automatically paste transcribed text at the current cursor position using clipboard + Ctrl+V simulation
- FR-6: The system must display a persistent system tray icon indicating app status (idle/recording)

**Configuration:**
- FR-7: The system must read configuration from `~/.config/voice-ctrl/config.json`
- FR-8: The system must support configurable settings: API key, max recording duration, audio feedback toggle, keyboard shortcut
- FR-9: The system must create default config file on first launch if it doesn't exist
- FR-10: Maximum recording duration must be configurable (default: 240 seconds / 4 minutes)

**Local STT:**
- FR-21: The system must support two STT providers: `openai` and `local`
- FR-22: The local provider must use faster-whisper for transcription
- FR-23: The system must scan default paths and a user-selected folder for model artifacts
- FR-24: The Settings UI must allow selecting provider, engine, and model
- FR-25: The system must support downloading a model by ID into a local cache
- FR-26: The system must fall back to OpenAI when local transcription fails

**Feedback:**
- FR-11: The system must change tray icon appearance when recording is active
- FR-12: The system must play audio beeps on start/stop recording (if enabled in config)
- FR-13: The system must show desktop notifications for errors with descriptive messages

**Error Handling:**
- FR-14: The system must handle API errors gracefully and show user-friendly error messages
- FR-15: The system must log errors to `~/.config/voice-ctrl/voice-ctrl.log`
- FR-16: The system must clean up temporary audio files after transcription (success or failure)
- FR-17: The system must validate API key format and show error if invalid

**Technical:**
- FR-18: The system must run as a background process/daemon on Ubuntu
- FR-19: The system must auto-start on login (optional, user-configurable)
- FR-20: The system must work on Ubuntu 20.04+ with GNOME desktop environment

## Non-Goals (Out of Scope)

- No support for multiple languages in MVP (uses Whisper's auto-detect)
- No speaker identification or diarization
- No custom voice commands or macros (just dictation)
- No audio editing or preview before transcription
- No support for other operating systems (Windows, macOS) in initial release
- No text-to-speech functionality
- No local model conversion or optimization pipelines
- No recording retry mechanism if API fails (just show error)
- No audio playback of recordings

## Design Considerations

**System Tray Icon:**
- Idle state: Microphone icon (gray/white)
- Recording state: Microphone icon with red dot or red background
- Use simple, recognizable iconography
- Tooltip should always show current state

**Desktop Notifications:**
- Use standard Ubuntu notification system (notify-send or equivalent)
- Keep messages concise and actionable
- Error notifications should persist longer than info notifications

**Config File Location:**
- Follow XDG Base Directory specification: `~/.config/voice-ctrl/`
- Use JSON for human readability and easy editing
- Include comments in README since JSON doesn't support comments natively

## Technical Considerations

**Technology Stack:**
- Language: Python 3.8+
- Audio recording: `pyaudio` or `sounddevice`
- Keyboard shortcuts: `pynput` or `keyboard` library
- System tray: `pystray` or `PyQt5` system tray
- Clipboard: `pyperclip`
- OpenAI API: `openai` Python SDK
- Desktop notifications: `plyer` or `notify2`

**Installation:**
- Standard Python package with `pip install`
- Systemd service file for auto-start (optional)
- Document dependencies: PortAudio (for pyaudio), Python 3.8+
- Consider AppImage or .deb package for easier distribution (Phase 3)

**API Key Security:**
- Store in config file with restricted permissions (chmod 600)
- Never log or display full API key
- Validate key format before making API calls

**Performance:**
- Minimize latency between stop recording and text insertion (<3 seconds typical)
- Efficient audio encoding to reduce API upload time
- Non-blocking UI - use threading for API calls

## Success Metrics

- User can dictate and insert text in <5 seconds from stop to paste
- Transcription accuracy matches OpenAI Whisper quality (95%+ for clear speech)
- App runs reliably for hours without crashes or memory leaks
- Zero false-positive shortcut triggers in normal typing
- Config file is understandable and modifiable by non-technical users

## Open Questions

- Should we support multiple simultaneous recordings? (Answer: No for MVP)
- Should there be a "cancel recording" option before transcription? (Nice to have, Phase 3)
- What happens if user switches windows while recording? (Continue recording, paste in new window)
- Should we save recording history? (No for MVP, privacy concern)
- Language selection or rely on Whisper auto-detect? (Auto-detect for MVP)

## Development Phases

**Phase 1 (MVP) - Core Functionality:**
- US-001 through US-006
- Hardcoded settings (4 min max, Ctrl+Shift+Space, no audio feedback)
- Manual config file editing only
- Target: Basic working dictation tool

**Phase 1.5 - Terminal Compatibility Fix:**
- US-007
- Replace Ctrl+V with Shift+Insert for better terminal support
- Target: Universal paste compatibility across GUI and CLI applications

**Phase 2 - Configuration & Polish:**
- US-008 through US-010
- Full configuration support
- Audio feedback
- Configurable shortcuts and duration
- Target: User-friendly, customizable tool

**Phase 3 - GUI Settings:**
- US-011 through US-012
- Settings GUI
- First-run setup wizard
- Target: Professional, polished application

**Phase 4 - Local STT:**
- US-022 through US-027
- Local transcription via faster-whisper
- Model discovery and download
- Fallback to OpenAI on failure

## Installation & Setup (Planned)

1. Clone repository / download package
2. Run setup script: `./install.sh` or `pip install -e .`
3. Create config file with API key: `~/.config/voice-ctrl/config.json`
4. Start app: `voice-ctrl` or add to startup applications
5. Press Ctrl+Shift+Space to test

## Verification Plan

After each phase:
- Manual testing: Record → Transcribe → Paste in various applications (terminal, Firefox, VS Code, LibreOffice)
- Test error scenarios: Invalid API key, network disconnect, no microphone, no audio
- Test configuration: Modify settings and verify they apply
- Performance test: Multiple recordings in succession, long recordings (near max duration)
- System resource check: CPU and memory usage while idle and recording
