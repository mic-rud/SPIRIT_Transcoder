#!/bin/bash
set -e

# URL of the file
URL="https://plenodb.jpeg.org/pc/8ilabs/8iVFBv2.7z"
FILENAME=$(basename "$URL")
DEST_DIR="./data"

# Download the file
wget -O "$DEST_DIR/$FILENAME" "$URL"

# Unzip
7z -x "$DEST_DIR/$FILENAME" -o "$DEST_DIR"

# Clean up
rm "$DEST_DIR/$FILENAME"