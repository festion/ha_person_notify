import time
import json
import yaml
import hashlib
import os
from flask import Flask, request, jsonify, render_template_string

CONFIG_FILE = "notification_config.yaml"
DEDUPLICATION_TTL = 300  # seconds
SENT_MESSAGES = {}

# Check if running in Home Assistant add-on
INGRESS_PATH = os.environ.get('INGRESS_PATH', '')

app = Flask(__name__)

# Simple HTML template for the status page
STATUS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Person-Based Notification Router</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #03a9f4; }
        .status { padding: 10px; background-color: #e8f5e9; border-radius: 4px; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Person-Based Notification Router</h1>
    <div class="status">Status: Running</div>
    <h2>API Documentation</h2>
    <p>Send notifications using a POST request to <code>/notify</code> with the following JSON payload:</p>
    <pre>
{
  "title": "Notification Title",
  "message": "Notification message content",
  "severity": "critical", // critical, warning, or info
  "audience": ["jeremy", "sarah"] // List of people to notify
}
    </pre>
</body>
</html>
"""

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return a default config if file can't be loaded
        return {
            "audiences": {},
            "severity_levels": ["info", "warning", "critical"]
        }

def get_hash(payload):
    base = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(base.encode()).hexdigest()

@app.route(f"{INGRESS_PATH}/", methods=["GET"])
@app.route("/", methods=["GET"])
def index():
    """Serve a simple status page with API documentation."""
    return render_template_string(STATUS_PAGE)

@app.route(f"{INGRESS_PATH}/notify", methods=["POST"])
@app.route("/notify", methods=["POST"])
def notify():
    """Handle notification requests."""
    if not request.is_json:
        return jsonify({"status": "error", "message": "Expected JSON payload"}), 400
        
    payload = request.get_json()
    
    # Validate required fields
    required_fields = ["title", "message", "severity", "audience"]
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        return jsonify({
            "status": "error", 
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400
    
    config = load_config()
    message_id = get_hash(payload)

    now = time.time()
    last_sent = SENT_MESSAGES.get(message_id, 0)
    if now - last_sent < DEDUPLICATION_TTL:
        return jsonify({
            "status": "duplicate", 
            "message": "Message already sent recently"
        }), 200

    title = payload.get("title")
    message = payload.get("message")
    severity = payload.get("severity")
    audience = payload.get("audience", [])

    SENT_MESSAGES[message_id] = now
    
    notification_count = 0
    for target in audience:
        target_config = config.get("audiences", {}).get(target, {})
        min_severity = target_config.get("min_severity", "low")
        try:
            if config.get("severity_levels", []).index(severity) >= config.get("severity_levels", []).index(min_severity):
                for service in target_config.get("services", []):
                    print(f"[{target.upper()}] {service} -> {title}: {message}")
                    notification_count += 1
        except ValueError:
            # Handle case where severity is not in the list
            print(f"Warning: Unknown severity level '{severity}'")

    return jsonify({
        "status": "ok", 
        "message": "Notification routed", 
        "delivered": notification_count
    }), 200

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors with a helpful message."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found. Use POST /notify for sending notifications."
    }), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors gracefully."""
    return jsonify({
        "status": "error",
        "message": "Server error occurred. Please check the logs."
    }), 500

if __name__ == "__main__":
    print(f"Starting Flask server on port 8732 with INGRESS_PATH={INGRESS_PATH}")
    app.run(host="0.0.0.0", port=8732)
