#!/bin/bash
set -e

echo "Cleaning up old builds..."
rm -rf build dist __pycache__

echo "Building DropCatcher.app..."
pyinstaller --noconfirm --windowed --name "DropCatcher" \
    --add-data "app/templates:app/templates" \
    --add-data "app/static:app/static" \
    --add-data ".env.template:." \
    launcher_mac.py

echo "Build complete! You can find the app in dist/DropCatcher.app"
