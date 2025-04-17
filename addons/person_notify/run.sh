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

# Export the ingress path for Flask
export INGRESS_PATH=$(cat /etc/nginx/ingress.conf 2>/dev/null | grep -oE '/api/hassio_ingress/[a-zA-Z0-9]+' || echo '')
echo "INGRESS_PATH set to: $INGRESS_PATH"

echo "Starting web server on port 8732..."
python3 main.py
