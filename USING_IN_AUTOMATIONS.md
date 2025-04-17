# Using the Person-Based Notification System in Home Assistant Automations

This guide explains how to integrate the Person-Based Notification System add-on with your Home Assistant automations, allowing you to send personalized notifications based on the preferences you've configured in the add-on.

## Prerequisites

- Home Assistant with the Person-Based Notification System add-on installed and configured
- Basic understanding of Home Assistant automations

## Setup Process

### 1. Create a REST Command

First, you need to add a REST command to your Home Assistant configuration to communicate with the notification add-on:

1. Open your `configuration.yaml` file
2. Add the following configuration (if you already have a `rest_command` section, add just the `person_notify` part):

```yaml
rest_command:
  person_notify:
    url: http://localhost:8732/notify
    method: POST
    content_type: 'application/json'
    payload: '{"title": "{{ title }}", "message": "{{ message }}", "severity": "{{ severity }}", "audience": {{ audience }} }'
```

3. Save the file and restart Home Assistant

### 2. Basic Usage in Automations

You can now use this REST command in your automations. Here's a basic example:

```yaml
automation:
  - alias: "Water Leak Alert"
    trigger:
      platform: state
      entity_id: binary_sensor.water_leak_detector
      to: 'on'
    action:
      - service: rest_command.person_notify
        data:
          title: "Water Leak Detected"
          message: "A water leak has been detected in the basement!"
          severity: "critical"
          audience: '["jeremy", "sarah"]'
```

This will send a critical notification to both Jeremy and Sarah when the water leak detector is triggered.

### 3. Using in the Automation GUI

You can also set this up through the Home Assistant GUI:

1. Go to Configuration → Automations
2. Click "Add Automation" or edit an existing automation
3. Add your desired trigger
4. For the action, select "Call service"
5. From the service dropdown, select "REST Command: person_notify"
6. In the service data field, add:

```yaml
title: "Your Notification Title"
message: "Your notification message here"
severity: "critical"  # or "warning" or "info"
audience: ["jeremy", "sarah"]  # List of people to notify
```

### 4. Creating Helper Scripts (Optional)

For more flexibility, you can create helper scripts:

```yaml
# In your scripts.yaml or configuration.yaml
script:
  notify_critical:
    alias: "Send Critical Notification"
    description: "Send a critical notification to specified users"
    fields:
      title:
        description: "Notification title"
        example: "Water Leak"
      message:
        description: "Notification message"
        example: "Water leak detected in basement"
      audience:
        description: "Who to notify (comma-separated)"
        example: "jeremy,sarah"
    sequence:
      - service: rest_command.person_notify
        data:
          title: "{{ title }}"
          message: "{{ message }}"
          severity: "critical"
          audience: "{{ audience.split(',') | list }}"
```

You can then use this script in your automations:

```yaml
automation:
  - alias: "Motion After Midnight"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door_motion
      to: 'on'
    condition:
      condition: time
      after: '00:00:00'
      before: '06:00:00'
    action:
      - service: script.notify_critical
        data:
          title: "Motion Detected"
          message: "Front door motion detected at {{ now().strftime('%H:%M') }}"
          audience: "jeremy,sarah"
```

## Advanced Use Cases

### Dynamic Audience Selection

You can use Home Assistant entities to dynamically determine who should receive notifications:

```yaml
automation:
  - alias: "Notify Who's Home"
    trigger:
      platform: state
      entity_id: binary_sensor.doorbell
      to: 'on'
    action:
      - service: rest_command.person_notify
        data:
          title: "Doorbell"
          message: "Someone is at the door"
          severity: "info"
          audience: >
            {% set people_home = [] %}
            {% for person in ['jeremy', 'sarah', 'kids'] %}
              {% if is_state('person.' + person, 'home') %}
                {% set people_home = people_home + [person] %}
              {% endif %}
            {% endfor %}
            {{ people_home }}
```

This automation will only notify people who are currently home when the doorbell rings.

### Different Severity Levels Based on Conditions

```yaml
automation:
  - alias: "Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.living_room_temperature
      above: 80
    action:
      - service: rest_command.person_notify
        data:
          title: "High Temperature"
          message: >
            Living room temperature is {{ states('sensor.living_room_temperature') }}°F
          severity: >
            {% if states('sensor.living_room_temperature')|float > 90 %}
              critical
            {% elif states('sensor.living_room_temperature')|float > 85 %}
              warning
            {% else %}
              info
            {% endif %}
          audience: '["jeremy"]'
```

This will send different severity levels of notifications based on how high the temperature is.

## Troubleshooting

If your notifications aren't working as expected:

1. Check the add-on logs for any error messages
2. Verify that the REST command is properly configured
3. Make sure the people you're trying to notify exist in the add-on's configuration
4. Check that the devices configured for each person are correct and available
5. Test sending a notification directly from the add-on's web interface

## API Reference

The notification API accepts the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| title | string | The title of the notification |
| message | string | The content of the notification |
| severity | string | One of: "critical", "warning", "info" |
| audience | array | List of people to notify, e.g., ["jeremy", "sarah"] |

## Examples

### Security Alert

```yaml
automation:
  - alias: "Security Alert"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door
      to: 'on'
    condition:
      condition: state
      entity_id: alarm_control_panel.home_alarm
      state: 'armed_away'
    action:
      - service: rest_command.person_notify
        data:
          title: "Security Alert"
          message: "Front door opened while alarm is armed!"
          severity: "critical"
          audience: '["jeremy", "sarah"]'
```

### Battery Low

```yaml
automation:
  - alias: "Battery Low"
    trigger:
      platform: numeric_state
      entity_id: sensor.front_door_battery
      below: 20
    action:
      - service: rest_command.person_notify
        data:
          title: "Battery Low"
          message: "Front door sensor battery is at {{ states('sensor.front_door_battery') }}%"
          severity: "warning"
          audience: '["jeremy"]'
```

### Package Delivery

```yaml
automation:
  - alias: "Package Delivered"
    trigger:
      platform: state
      entity_id: binary_sensor.mailbox
      to: 'on'
    action:
      - service: rest_command.person_notify
        data:
          title: "Package Delivered"
          message: "A package has been delivered to your mailbox"
          severity: "info"
          audience: '["jeremy", "sarah"]'
```
