#!/bin/bash
set -e

# Build script for creating voice-ctrl .deb package

echo "Building VoiceControl .deb package..."

# Clean up previous build
rm -rf packaging/voice-ctrl/opt/voice-ctrl/*
rm -f voice-ctrl.deb

# Copy application files to package directory
echo "Copying application files..."
cp -r src packaging/voice-ctrl/opt/voice-ctrl/
cp requirements.txt packaging/voice-ctrl/opt/voice-ctrl/
cp README.md packaging/voice-ctrl/opt/voice-ctrl/

# Remove __pycache__ directories
find packaging/voice-ctrl/opt/voice-ctrl -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Build the package
echo "Building package..."
dpkg-deb --build packaging/voice-ctrl

# Move the package to root directory
mv packaging/voice-ctrl.deb voice-ctrl.deb

echo ""
echo "✓ Package built successfully: voice-ctrl.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i voice-ctrl.deb"
echo "  sudo apt-get install -f  # Install dependencies if needed"
echo ""
echo "To uninstall:"
echo "  sudo apt remove voice-ctrl"
echo ""
