# Home Assistant Person-Based Notification System

This document outlines the design and implementation of a person-based notification system for Home Assistant that allows sending notifications based on severity levels.

## Design Goals

- Notify people, not just devices
- Support different severity levels (Critical, Warning, Info)
- Allow each user to set their own notification preferences per severity level
- Provide a centralized notification service that respects user preferences
- Log all notifications for auditing purposes

## System Components

### 1. Severity Levels

The system is built around three severity levels:

- **Critical**: Immediate attention required (fire, security breach, water leak)
- **Warning**: Important but not urgent (low battery, temperature thresholds)
- **Info**: Routine information (package delivered, person arrived home)

### 2. Person Entities

Each person in the household has their own person entity in Home Assistant, allowing the system to target specific people rather than just devices.

### 3. User Preferences Configuration

Each user can configure their notification preferences using input helpers:

```yaml
# User notification preferences configuration
input_select:
  jeremy_critical_notification:
    name: "Jeremy - Critical Notifications"
    options:
      - "All Devices"
      - "Mobile Only"
      - "Desktop Only"
      - "None"
    initial: "All Devices"
  
  jeremy_warning_notification:
    name: "Jeremy - Warning Notifications"
    options:
      - "All Devices"
      - "Mobile Only"
      - "Desktop Only"
      - "None"
    initial: "Mobile Only"
  
  jeremy_info_notification:
    name: "Jeremy - Info Notifications"
    options:
      - "All Devices"
      - "Mobile Only"
      - "Desktop Only"
      - "Log Only"
      - "None"
    initial: "Log Only"
```