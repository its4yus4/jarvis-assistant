#!/bin/bash

# Auto-setup script for Jarvis
echo "🤖 Jarvis Assistant - Auto Setup"

# Create necessary directories
mkdir -p logs images examples

# Create empty log file
touch logs/jarvis.log 2>/dev/null || {
    echo "⚠️  Could not create log file, continuing anyway..."
}

# Set permissions
chmod 666 logs/jarvis.log 2>/dev/null || true

echo "✅ Environment ready!"
echo "🚀 Starting Jarvis..."

# Run jarvis
python3 jarvis.py "$@"
