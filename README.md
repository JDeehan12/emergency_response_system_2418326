# Emergency Response System  
**SDLC Method**: Agile
**Version**: Version 1.5.0
**Last Updated**: 2025-04-24

## Overview  
A console-based emergency management system that intelligently allocates response resources based on:
- Incident priority (high/medium/low)
- Resource type matching
- Geographic proximity (zone-based)
- Dynamic reallocation capabilities
- Incident age prioritisation (newer incidents take precedence)

## Key Improvements in v1.5.0
- Timestamp-based incident prioritisation: Newer high-priority incidents now take precedence
- Enhanced allocation fairness: Clear rules for competing same-priority incidents
- Improved resource reallocation: Better handling of dynamic emergency scenarios
- Bug fixes: Resolved resource allocation edge cases

## Project Structure (MVC Architecture)

emergency_response_system/
├── models/ # Data models and business logic
│ ├── incident.py # Incident class with priority and timestamp tracking
│ ├── resource.py # Resource class with availability management
│ └── init.py
├── views/ # User interface
│ ├── console_ui.py # Menu-driven console interface
│ └── init.py
├── controllers/ # Application logic
│ ├── dispatcher.py # Enhanced smart allocation engine
│ ├── main_controller.py
│ └── init.py
├── tests/ # Test suite
│ ├── unit/ # Component tests
│ ├── integration/ # System workflow tests
│ └── init.py
├── main.py # Application entry
└── README.md

## Core Features
### Intelligent Allocation
- Priority-based dispatching (high > medium > low)
- Timestamp-based prioritisation for same-priority incidents
- Automatic reallocation for critical incidents
- Zone-based proximity calculations
- Resource type matching (ambulance/fire/police)

### Incident Management
- Dynamic priority adjustment
- Status tracking (unassigned/assigned)
- Multi-resource requirements support
- Age-based prioritisation tracking

### Testing Framework
- Unit tests for all components
- Integration tests for full workflows
- Edge case coverage:
  - Resource contention scenarios
  - Priority escalation cases
  - Timestamp-based prioritisation
  - Failure rollback testing

## Usage
```bash
# Run all tests (unit + integration)
python -m unittest discover tests

# Start application
python main.py

# Development workflow
git checkout -b feature/feature-name   # Create branch
python -m unittest tests/test_module.py  # Verify changes
git add -p                           # Review changes
git commit -m "feat: detailed message"
git push origin feature/feature-name

# Version tagging
git tag -a v1.5.0 -m "Version 1.5.0 with timestamp-based prioritisation"
git push origin v1.5.0
