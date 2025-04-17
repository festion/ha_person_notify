import time
import json
import yaml
import hashlib
import os
from flask import Flask, request, jsonify, render_template_string, redirect, url_for

CONFIG_FILE = "notification_config.yaml"
DEDUPLICATION_TTL = 300  # seconds
SENT_MESSAGES = {}

# Check if running in Home Assistant add-on
INGRESS_PATH = os.environ.get('INGRESS_PATH', '')

app = Flask(__name__)

# Main web UI template with CSS and JavaScript
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Person-Based Notification System</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            line-height: 1.6;
            color: #333;
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1, h2, h3 { color: #03a9f4; }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: 1px solid transparent;
            margin-bottom: -1px;
        }
        .tab.active {
            border: 1px solid #ddd;
            border-bottom-color: white;
            background: white;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        select, input, button {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background-color: #03a9f4;
            color: white;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #0288d1;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .device-list {
            list-style-type: none;
            padding: 0;
        }
        .device-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .badge {
            display: inline-block;
            padding: 3px 7px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-info { background-color: #e8f5e9; color: #2e7d32; }
        .badge-warning { background-color: #fff8e1; color: #ff8f00; }
        .badge-critical { background-color: #ffebee; color: #c62828; }
        .status-message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .status-success { background-color: #e8f5e9; color: #2e7d32; }
        .status-error { background-color: #ffebee; color: #c62828; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <h1>Person-Based Notification System</h1>
    
    <div class="tabs">
        <div class="tab active" data-tab="preferences">Notification Preferences</div>
        <div class="tab" data-tab="devices">Device Management</div>
        <div class="tab" data-tab="test">Test Notifications</div>
        <div class="tab" data-tab="api">API Documentation</div>
    </div>
    
    <div id="status-message" class="status-message hidden"></div>
    
    <div id="preferences" class="tab-content active">
        <div class="card">
            <h2>User Notification Preferences</h2>
            <p>Configure how each person receives notifications based on severity level.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Person</th>
                        <th>Critical Notifications</th>
                        <th>Warning Notifications</th>
                        <th>Info Notifications</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="preferences-table">
                    <!-- Populated by JavaScript -->
                </tbody>
            </table>
            
            <h3>Add New Person</h3>
            <div class="form-group">
                <label for="new-person-name">Person Name:</label>
                <input type="text" id="new-person-name" placeholder="Enter name">
            </div>
            <button id="add-person-btn">Add Person</button>
        </div>
    </div>
    
    <div id="devices" class="tab-content">
        <div class="card">
            <h2>Device Management</h2>
            <p>Manage notification devices for each person.</p>
            
            <div class="form-group">
                <label for="device-person-select">Select Person:</label>
                <select id="device-person-select">
                    <!-- Populated by JavaScript -->
                </select>
            </div>
            
            <h3>Devices</h3>
            <div id="device-lists">
                <div>
                    <h4>All Devices</h4>
                    <ul id="all-devices-list" class="device-list">
                        <!-- Populated by JavaScript -->
                    </ul>
                    <div class="form-group">
                        <input type="text" id="add-all-device" placeholder="notify.new_device">
                        <button id="add-all-device-btn">Add Device</button>
                    </div>
                </div>
                
                <div>
                    <h4>Mobile Devices</h4>
                    <ul id="mobile-devices-list" class="device-list">
                        <!-- Populated by JavaScript -->
                    </ul>
                    <div class="form-group">
                        <input type="text" id="add-mobile-device" placeholder="notify.mobile_app_phone">
                        <button id="add-mobile-device-btn">Add Device</button>
                    </div>
                </div>
                
                <div>
                    <h4>Desktop Devices</h4>
                    <ul id="desktop-devices-list" class="device-list">
                        <!-- Populated by JavaScript -->
                    </ul>
                    <div class="form-group">
                        <input type="text" id="add-desktop-device" placeholder="notify.laptop">
                        <button id="add-desktop-device-btn">Add Device</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="test" class="tab-content">
        <div class="card">
            <h2>Test Notifications</h2>
            <p>Send test notifications to verify your configuration.</p>
            
            <div class="form-group">
                <label for="test-person">Person to Notify:</label>
                <select id="test-person">
                    <!-- Populated by JavaScript -->
                </select>
            </div>
            
            <div class="form-group">
                <label for="test-severity">Severity Level:</label>
                <select id="test-severity">
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="critical">Critical</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="test-title">Notification Title:</label>
                <input type="text" id="test-title" value="Test Notification">
            </div>
            
            <div class="form-group">
                <label for="test-message">Message:</label>
                <input type="text" id="test-message" value="This is a test notification">
            </div>
            
            <button id="send-test-btn">Send Test Notification</button>
        </div>
    </div>
    
    <div id="api" class="tab-content">
        <div class="card">
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
            
            <h3>Example with curl</h3>
            <pre>
curl -X POST http://your-homeassistant:8732/notify \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Water Leak",
    "message": "Water leak detected in basement",
    "severity": "critical",
    "audience": ["jeremy"]
  }'
            </pre>
        </div>
    </div>

    <script>
        // Load configuration data
        let config = {};
        
        // Initialize the UI
        document.addEventListener('DOMContentLoaded', function() {
            // Tab switching
            document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                    
                    this.classList.add('active');
                    document.getElementById(this.dataset.tab).classList.add('active');
                });
            });
            
            // Load config
            fetchConfig();
            
            // Set up event listeners
            document.getElementById('add-person-btn').addEventListener('click', addPerson);
            document.getElementById('device-person-select').addEventListener('change', loadDevicesForPerson);
            document.getElementById('add-all-device-btn').addEventListener('click', () => addDevice('all'));
            document.getElementById('add-mobile-device-btn').addEventListener('click', () => addDevice('mobile'));
            document.getElementById('add-desktop-device-btn').addEventListener('click', () => addDevice('desktop'));
            document.getElementById('send-test-btn').addEventListener('click', sendTestNotification);
        });
        
        // Fetch configuration
        function fetchConfig() {
            fetch('/config')
                .then(response => response.json())
                .then(data => {
                    config = data;
                    updatePreferencesTable();
                    updatePersonSelects();
                })
                .catch(error => {
                    showStatusMessage('Error loading configuration: ' + error.message, 'error');
                });
        }
        
        // Update the preferences table
        function updatePreferencesTable() {
            const tbody = document.getElementById('preferences-table');
            tbody.innerHTML = '';
            
            const preferenceOptions = ['All Devices', 'Mobile Only', 'Desktop Only', 'Log Only', 'None'];
            
            for (const person in config.audiences) {
                const row = document.createElement('tr');
                
                // Person name
                const nameCell = document.createElement('td');
                nameCell.textContent = person;
                row.appendChild(nameCell);
                
                // Create preference selects
                ['critical', 'warning', 'info'].forEach(severity => {
                    const cell = document.createElement('td');
                    const select = document.createElement('select');
                    select.id = `${person}-${severity}`;
                    
                    preferenceOptions.forEach(option => {
                        const optEl = document.createElement('option');
                        optEl.value = option.replace(' ', '_').toLowerCase();
                        optEl.textContent = option;
                        select.appendChild(optEl);
                    });
                    
                    // Set current value
                    const currentPref = config.audiences[person][severity + '_notification'] || 'none';
                    select.value = currentPref;
                    
                    select.addEventListener('change', () => updatePreference(person, severity, select.value));
                    
                    cell.appendChild(select);
                    row.appendChild(cell);
                });
                
                // Actions
                const actionsCell = document.createElement('td');
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Delete';
                deleteBtn.addEventListener('click', () => deletePerson(person));
                actionsCell.appendChild(deleteBtn);
                row.appendChild(actionsCell);
                
                tbody.appendChild(row);
            }
        }
        
        // Update person select dropdowns
        function updatePersonSelects() {
            const personSelects = [
                document.getElementById('device-person-select'),
                document.getElementById('test-person')
            ];
            
            personSelects.forEach(select => {
                select.innerHTML = '';
                
                for (const person in config.audiences) {
                    const option = document.createElement('option');
                    option.value = person;
                    option.textContent = person;
                    select.appendChild(option);
                }
                
                if (select.id === 'device-person-select' && select.options.length > 0) {
                    loadDevicesForPerson();
                }
            });
        }
        
        // Load devices for selected person
        function loadDevicesForPerson() {
            const select = document.getElementById('device-person-select');
            const person = select.value;
            
            if (!person) return;
            
            const personConfig = config.audiences[person];
            
            // Update device lists
            updateDeviceList('all', personConfig.devices?.all || []);
            updateDeviceList('mobile', personConfig.devices?.mobile || []);
            updateDeviceList('desktop', personConfig.devices?.desktop || []);
        }
        
        // Update a device list
        function updateDeviceList(type, devices) {
            const list = document.getElementById(`${type}-devices-list`);
            list.innerHTML = '';
            
            devices.forEach(device => {
                const li = document.createElement('li');
                li.className = 'device-item';
                
                const deviceName = document.createElement('span');
                deviceName.textContent = device;
                
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Remove';
                deleteBtn.addEventListener('click', () => removeDevice(type, device));
                
                li.appendChild(deviceName);
                li.appendChild(deleteBtn);
                list.appendChild(li);
            });
        }
        
        // Add a new person
        function addPerson() {
            const nameInput = document.getElementById('new-person-name');
            const name = nameInput.value.trim().toLowerCase();
            
            if (!name) {
                showStatusMessage('Please enter a name for the new person', 'error');
                return;
            }
            
            if (config.audiences[name]) {
                showStatusMessage(`Person "${name}" already exists`, 'error');
                return;
            }
            
            // Add to config
            config.audiences[name] = {
                critical_notification: 'all_devices',
                warning_notification: 'mobile_only',
                info_notification: 'log_only',
                devices: {
                    all: [],
                    mobile: [],
                    desktop: []
                }
            };
            
            // Save config
            saveConfig();
            
            // Clear input
            nameInput.value = '';
        }
        
        // Delete a person
        function deletePerson(person) {
            if (confirm(`Are you sure you want to delete ${person}?`)) {
                delete config.audiences[person];
                saveConfig();
            }
        }
        
        // Update notification preference
        function updatePreference(person, severity, value) {
            config.audiences[person][severity + '_notification'] = value;
            saveConfig();
        }
        
        // Add a device
        function addDevice(type) {
            const input = document.getElementById(`add-${type}-device`);
            const device = input.value.trim();
            
            if (!device) {
                showStatusMessage(`Please enter a device entity ID`, 'error');
                return;
            }
            
            const personSelect = document.getElementById('device-person-select');
            const person = personSelect.value;
            
            if (!person) return;
            
            // Initialize devices object if it doesn't exist
            if (!config.audiences[person].devices) {
                config.audiences[person].devices = { all: [], mobile: [], desktop: [] };
            }
            
            // Add to list if not already present
            if (!config.audiences[person].devices[type].includes(device)) {
                config.audiences[person].devices[type].push(device);
                saveConfig();
            }
            
            // Clear input
            input.value = '';
        }
        
        // Remove a device
        function removeDevice(type, device) {
            const personSelect = document.getElementById('device-person-select');
            const person = personSelect.value;
            
            if (!person) return;
            
            const devices = config.audiences[person].devices[type];
            const index = devices.indexOf(device);
            
            if (index !== -1) {
                devices.splice(index, 1);
                saveConfig();
            }
        }
        
        // Save configuration
        function saveConfig() {
            fetch('/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    showStatusMessage('Configuration saved successfully', 'success');
                    fetchConfig(); // Reload config
                } else {
                    showStatusMessage(`Error: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                showStatusMessage('Error saving configuration: ' + error.message, 'error');
            });
        }
        
        // Send a test notification
        function sendTestNotification() {
            const person = document.getElementById('test-person').value;
            const severity = document.getElementById('test-severity').value;
            const title = document.getElementById('test-title').value;
            const message = document.getElementById('test-message').value;
            
            if (!person || !title || !message) {
                showStatusMessage('Please fill in all fields', 'error');
                return;
            }
            
            fetch('/notify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    message: message,
                    severity: severity,
                    audience: [person]
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    showStatusMessage(`Test notification sent to ${person}`, 'success');
                } else {
                    showStatusMessage(`Error: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                showStatusMessage('Error sending notification: ' + error.message, 'error');
            });
        }
        
        // Show status message
        function showStatusMessage(message, type) {
            const statusEl = document.getElementById('status-message');
            statusEl.textContent = message;
            statusEl.className = `status-message status-${type}`;
            
            // Show message
            statusEl.classList.remove('hidden');
            
            // Hide after 5 seconds
            setTimeout(() => {
                statusEl.classList.add('hidden');
            }, 5000);
        }
    </script>
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

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_hash(payload):
    base = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(base.encode()).hexdigest()

@app.route(f"{INGRESS_PATH}/", methods=["GET"])
@app.route("/", methods=["GET"])
def index():
    """Serve the main web UI."""
    return render_template_string(MAIN_TEMPLATE)

@app.route(f"{INGRESS_PATH}/config", methods=["GET"])
@app.route("/config", methods=["GET"])
def get_config():
    """Return the current configuration."""
    return jsonify(load_config())

@app.route(f"{INGRESS_PATH}/config", methods=["POST"])
@app.route("/config", methods=["POST"])
def update_config():
    """Update the configuration."""
    if not request.is_json:
        return jsonify({"status": "error", "message": "Expected JSON payload"}), 400
        
    config = request.get_json()
    
    # Validate config structure (basic validation)
    if "audiences" not in config or "severity_levels" not in config:
        return jsonify({"status": "error", "message": "Invalid configuration structure"}), 400
    
    if save_config(config):
        return jsonify({"status": "ok", "message": "Configuration saved"})
    else:
        return jsonify({"status": "error", "message": "Failed to save configuration"}), 500

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
        pref_key = f"{severity}_notification"
        preference = target_config.get(pref_key, "none")
        
        print(f"Notifying {target} with {severity} priority (preference: {preference})")
        
        # Always log the notification
        print(f"[LOG] Notification for {target}: [{severity.upper()}] {title} - {message}")
        
        # Skip further processing if preference is "None" or "Log Only"
        if preference in ["none", "log_only"]:
            continue
        
        # Get devices based on preference
        devices = []
        if preference == "all_devices":
            devices = target_config.get("devices", {}).get("all", [])
        elif preference == "mobile_only":
            devices = target_config.get("devices", {}).get("mobile", [])
        elif preference == "desktop_only":
            devices = target_config.get("devices", {}).get("desktop", [])
        
        # Send to devices (in a real implementation, this would call Home Assistant services)
        for device in devices:
            print(f"[{target.upper()}] Sending to {device} -> {title}: {message}")
            notification_count += 1

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
        "message": "Endpoint not found. Use POST /notify for sending notifications or visit the web UI."
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
