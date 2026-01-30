# PRD: Local Speech-to-Text (STT) Support

## Introduction

Add local speech-to-text transcription so users can avoid API costs and reuse already-downloaded local Whisper models. The app should detect existing models from common locations or user-selected folders and allow choosing a local engine in Settings. If local transcription fails or no model is found, the system should show an error and fall back to the OpenAI Whisper API.

## Goals

- Provide cost-saving local transcription with a popular, reliable engine (faster-whisper first).
- Detect existing local models automatically and via user-specified folder scans.
- Let users select local models in Settings with a clear UI.
- Fall back to OpenAI Whisper API on failure while notifying the user.
- Support downloading a local model from scratch within the app.

## User Stories

### US-001: Add local STT config and defaults
**Description:** As a user, I want local STT settings saved in config so my choices persist across restarts.

**Acceptance Criteria:**
- [ ] Config file includes new fields: `stt_provider`, `local_engine`, `local_model_path`, `local_model_id`, `local_scan_paths`.
- [ ] Defaults are set on first run and migrated into existing configs.
- [ ] `stt_provider` supports `openai` and `local` values.
- [ ] Invalid config values trigger a user notification and revert to defaults.

### US-002: Local STT engine wrapper (faster-whisper)
**Description:** As a user, I want transcription to run with faster-whisper so I can avoid API costs.

**Acceptance Criteria:**
- [ ] A new local transcriber uses faster-whisper for transcription from WAV input.
- [ ] Engine supports model path and model ID (Hugging Face model name) inputs.
- [ ] Transcription returns a plain text string or `None` on failure.
- [ ] Errors are logged and surfaced via desktop notification.
- [ ] OpenAI transcription path remains unchanged when `stt_provider` is `openai`.

### US-003: Model discovery by scanning folders
**Description:** As a user, I want the app to scan for existing local models so I can reuse downloads from other apps.

**Acceptance Criteria:**
- [ ] On demand, scan default paths (e.g., `~/.cache`, `~/.local/share`, `~/Downloads`).
- [ ] Allow scanning a user-selected folder.
- [ ] Detected models are shown in Settings as selectable options.
- [ ] Each detected model includes a label (model name) and path.
- [ ] Scanning does not block the UI (runs in a background thread).
- [ ] **Verify in browser using dev-browser skill**.

### US-004: Settings UI for local STT selection
**Description:** As a user, I want to configure local STT in the Settings window so I can easily switch providers and models.

**Acceptance Criteria:**
- [ ] Settings includes a provider selector: `OpenAI` or `Local`.
- [ ] When `Local` is selected, show engine selector (default: faster-whisper).
- [ ] Show model dropdown/radio list populated by scan results.
- [ ] Provide buttons: "Scan Default Paths" and "Scan Folder...".
- [ ] Provide a field for `model_id` with a "Download Model" action.
- [ ] Saving settings updates config immediately.
- [ ] **Verify in browser using dev-browser skill**.

### US-005: Model download from scratch
**Description:** As a user, I want to download a local model by name so I can use local STT without manual setup.

**Acceptance Criteria:**
- [ ] Given a model ID (e.g., `openai/whisper-small`), the app downloads it to a local cache.
- [ ] Progress or status is shown in Settings during download.
- [ ] Downloaded model appears in the model selection list.
- [ ] Errors (network, invalid model ID) show a notification.
- [ ] **Verify in browser using dev-browser skill**.

### US-006: Fallback to OpenAI on local failure
**Description:** As a user, I want the app to fall back to OpenAI when local transcription fails so I can still get results.

**Acceptance Criteria:**
- [ ] If local transcription fails, notify the user with a concise error.
- [ ] Automatically retry with OpenAI Whisper API.
- [ ] If OpenAI also fails, show a single final error notification.
- [ ] History logging still records the transcription when fallback succeeds.

## Functional Requirements

- FR-1: The system must support two STT providers: `openai` and `local`.
- FR-2: The local provider must use faster-whisper for transcription.
- FR-3: The system must scan default paths and a user-selected folder for model artifacts.
- FR-4: The Settings UI must allow selecting provider, engine, and model.
- FR-5: The system must support downloading a model by ID into a local cache.
- FR-6: The system must fall back to OpenAI when local transcription fails.

## Non-Goals (Out of Scope)

- No text-to-speech functionality.
- No multi-language model management UI beyond choosing a model.
- No model conversion or optimization pipelines.
- No GPU/CPU tuning controls in v1.

## Design Considerations

- Keep UI changes inside the existing Settings window.
- Use a dropdown or radio list for detected models to keep selection clear.
- Show a small status line for scans/downloads (Idle, Scanning, Downloading, Error).

## Technical Considerations

- Consider `faster-whisper` Python dependency and model cache handling.
- Model discovery should be path-based and not assume a single vendor layout.
- Use background threads for scanning and downloads to avoid UI freezes.
- Define a normalized model record: `{name, path, source}`.

## Success Metrics

- Users can select and run local transcription without API usage.
- Existing models in common folders are discovered and selectable.
- Local failure automatically falls back to OpenAI with clear notification.

## Open Questions

- Which default folders should be prioritized first?
- Should we support more engines after faster-whisper (e.g., whisper.cpp)?
- Should model downloads be limited to a curated list vs free-form IDs?
