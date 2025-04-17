# Home Assistant Person-Based Notification System

A flexible notification system for Home Assistant that allows sending notifications to people based on severity levels and personal preferences.

## Features

- Notify people, not just devices
- Support different severity levels (Critical, Warning, Info)
- Allow each user to set their own notification preferences per severity level
- Provide a centralized notification service that respects user preferences
- Log all notifications for auditing purposes
- Fully integrated with Home Assistant entities and services

## Installation

To install this add-on, you need to add the repository to your Home Assistant instance:

1. Go to Settings → Add-ons → Add-on Store
2. Click the three dots menu in the top right corner
3. Select "Repositories"
4. Add the repository URL: https://github.com/festion/ha_person_notify
5. Click "Add"
6. The "Person-Based Notification Router" add-on should now appear in your add-on store
7. Click on it and then click "Install"

## Configuration

After installing the add-on:

1. Start the add-on
2. Access the web interface by clicking "Open Web UI"
3. The system will automatically detect your Home Assistant users
4. For each user, you can configure:
   - Notification preferences for each severity level (Critical, Warning, Info)
   - Devices to use for different types of notifications

## Usage in Automations

This notification system can be used directly in your Home Assistant automations, allowing you to send personalized notifications based on the preferences you've configured.

For detailed instructions, see the [Using in Automations](USING_IN_AUTOMATIONS.md) guide.

Basic example:

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

## Documentation

- [CLAUDE.md](CLAUDE.md) - Initial design document
- [USING_IN_AUTOMATIONS.md](USING_IN_AUTOMATIONS.md) - Detailed guide for using in Home Assistant automations

## Versions

- Version 1.0.9 - Current stable version with Home Assistant integration and user preference management

## Development

For developers who want to contribute to this project:

1. Clone the repository
2. Make your changes
3. Test your changes in a Home Assistant environment
4. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
