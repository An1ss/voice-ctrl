"""Model scanner module for discovering local Whisper models."""

import os
import logging
from pathlib import Path
import threading


class ModelScanner:
    """Scans directories for local Whisper model files."""

    def __init__(self, log_path=None):
        """Initialize the model scanner.

        Args:
            log_path: Path to log file (optional)
        """
        self.log_path = log_path
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _setup_logging(self):
        """Configure logging to file."""
        if self.log_path:
            logging.basicConfig(
                filename=str(self.log_path),
                level=logging.ERROR,
                format='[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                force=True
            )

    def scan_default_paths(self, callback=None):
        """Scan default paths for Whisper models in a background thread.

        Default paths include:
        - ~/.cache/huggingface/hub
        - ~/.cache/whisper
        - ~/.local/share
        - ~/Downloads

        Args:
            callback: Optional callback function(models_list) called when scan completes

        Returns:
            Threading object for the background scan
        """
        default_paths = [
            Path.home() / ".cache" / "huggingface" / "hub",
            Path.home() / ".cache" / "whisper",
            Path.home() / ".local" / "share",
            Path.home() / "Downloads"
        ]

        return self.scan_paths(default_paths, callback)

    def scan_paths(self, paths, callback=None):
        """Scan specified paths for Whisper models in a background thread.

        Args:
            paths: List of Path objects or strings to scan
            callback: Optional callback function(models_list) called when scan completes

        Returns:
            Threading object for the background scan
        """
        def scan_worker():
            models = []
            for path in paths:
                path_obj = Path(path) if isinstance(path, str) else path
                found = self._scan_directory(path_obj)
                models.extend(found)

            # Remove duplicates based on path
            unique_models = []
            seen_paths = set()
            for model in models:
                if model['path'] not in seen_paths:
                    unique_models.append(model)
                    seen_paths.add(model['path'])

            if callback:
                callback(unique_models)

            return unique_models

        # Run scan in background thread
        thread = threading.Thread(target=scan_worker, daemon=True)
        thread.start()
        return thread

    def scan_folder_sync(self, folder_path):
        """Synchronously scan a specific folder for Whisper models.

        Args:
            folder_path: Path to folder to scan (Path object or string)

        Returns:
            List of model dictionaries with 'name' and 'path' keys
        """
        path_obj = Path(folder_path) if isinstance(folder_path, str) else folder_path
        return self._scan_directory(path_obj)

    def _scan_directory(self, directory):
        """Scan a directory for Whisper model files.

        Looks for:
        - Directories containing model.bin or pytorch_model.bin
        - Directories with "whisper" in the name
        - Directories with faster-whisper model structure (config.json + model.bin)

        Args:
            directory: Path object to scan

        Returns:
            List of model dictionaries with 'name' and 'path' keys
        """
        models = []

        if not directory.exists() or not directory.is_dir():
            return models

        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(directory):
                root_path = Path(root)

                # Check if this directory contains model files
                if self._is_model_directory(root_path, files):
                    model_name = self._extract_model_name(root_path)
                    models.append({
                        'name': model_name,
                        'path': str(root_path)
                    })

                # Limit depth to avoid scanning too deep (max 5 levels)
                if root_path.relative_to(directory).parts.__len__() >= 5:
                    dirs.clear()  # Don't descend further

        except PermissionError:
            # Skip directories we don't have permission to read
            self.logger.warning(f"Permission denied scanning: {directory}")
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")

        return models

    def _is_model_directory(self, directory, files):
        """Check if a directory contains Whisper model files.

        Args:
            directory: Path object of directory
            files: List of filenames in the directory

        Returns:
            True if this appears to be a model directory, False otherwise
        """
        # Check for common model files
        model_files = [
            'model.bin',
            'pytorch_model.bin',
            'model.safetensors',
            'model.onnx'
        ]

        has_model_file = any(f in files for f in model_files)

        # Check for config files that indicate a model
        config_files = ['config.json', 'model.json']
        has_config = any(f in files for f in config_files)

        # Check for "whisper" in directory name
        has_whisper_in_name = 'whisper' in directory.name.lower()

        # A valid model directory should have either:
        # 1. A model file + config file
        # 2. A model file and "whisper" in the path
        if has_model_file and (has_config or has_whisper_in_name):
            return True

        # Also check for faster-whisper vocabulary file
        has_vocabulary = 'vocabulary.txt' in files
        if has_model_file and has_vocabulary:
            return True

        return False

    def _extract_model_name(self, model_path):
        """Extract a human-readable model name from the path.

        Args:
            model_path: Path object of the model directory

        Returns:
            String name for the model
        """
        # Check if this is a Hugging Face hub model (has "models--" in path)
        path_str = str(model_path)
        if 'models--' in path_str:
            # Extract the model name from the path
            # e.g., models--Systran--faster-whisper-small
            parts = model_path.parts
            for part in parts:
                if part.startswith('models--'):
                    # Clean up the model name
                    model_name = part.replace('models--', '').replace('--', '/')
                    # Extract size if present
                    sizes = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
                    for size in sizes:
                        if size in model_name.lower():
                            return f"Faster-Whisper {size.title()}"
                    return model_name

        # Get the directory name
        dir_name = model_path.name

        # Clean up common prefixes/suffixes
        name = dir_name.replace('models--', '').replace('--', '/')
        name = name.replace('snapshots', '').replace('_', ' ')

        # Look for model size indicators
        sizes = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
        for size in sizes:
            if size in name.lower():
                # Try to construct a cleaner name
                if 'whisper' in name.lower():
                    return f"Whisper {size.title()}"
                else:
                    return f"{name} ({size})"

        # If path contains "whisper", include it
        if 'whisper' in str(model_path).lower():
            parts = model_path.parts
            # Look for meaningful parts
            for part in reversed(parts):
                if 'whisper' in part.lower() and part != dir_name:
                    return f"{part}/{dir_name}"

        # Fallback to directory name
        if len(name) > 50:
            name = name[:47] + "..."

        return name if name else dir_name
