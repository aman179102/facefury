#!/bin/bash
# Build FaceFury Android APK using Docker (most reliable method)
#
# Prerequisites:
#   - Docker installed and running
#   - Internet connection (downloads ~2GB on first run)
#
# Usage:
#   chmod +x build_apk.sh
#   ./build_apk.sh
#
# The APK will be output to the bin/ directory.

set -e

echo "================================================"
echo "  FaceFury Android APK Builder"
echo "  Using Docker for reliable cross-compilation"
echo "================================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo ""
echo "Building APK with buildozer Docker image..."
echo "This may take 20-40 minutes on first run."
echo ""

docker run --rm \
    -v "$(pwd)":/home/user/hostcwd \
    -w /home/user/hostcwd \
    kivy/buildozer:latest \
    android debug

echo ""
echo "================================================"
echo "  Build complete!"
echo "  APK location: bin/"
echo ""
ls -la bin/*.apk 2>/dev/null || echo "  (check bin/ directory for the APK)"
echo "================================================"
echo ""
echo "Transfer the APK to your Android 6+ device and install."
echo "You may need to enable 'Install from unknown sources' in Settings."
