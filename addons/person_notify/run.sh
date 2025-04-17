#!/bin/bash
set -e

echo "Starting Person-Based Notification Router..."
echo "Checking configuration..."

if [ -f "notification_config.yaml" ]; then
    echo "Configuration found."
else
    echo "Configuration not found, creating default..."
    cp /app/notification_config.yaml.default /app/notification_config.yaml
fi

# Check permissions
if [ -z "$SUPERVISOR_TOKEN" ]; then
    echo "WARNING: SUPERVISOR_TOKEN not found. Home Assistant API access will not work."
    echo "Make sure you have enabled API access in the add-on configuration."
fi

echo "Starting web server on port 8732..."
python3 main.py
