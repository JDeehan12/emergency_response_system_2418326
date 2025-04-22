# Emergency Response System  
**SDLC Method**: Agile (iterative development in sprints)  
**Version**: Version 1.4.0
**Last Updated**: 2025-04-17

## Overview  
A console-based emergency management system that intelligently allocates response resources based on:
- Incident priority (high/medium/low)
- Resource type matching
- Geographic proximity (zone-based)
- Dynamic reallocation capabilities

## Key Improvements in v1.4.0
- Full incident IDs visible in all tables
- Improved table column spacing
- Cleaner border formatting
- All tests updated for new formats

## Project Structure (MVC Architecture)

emergency_response_system/
├── models/ # Data models and business logic
│ ├── incident.py # Incident class with priority tracking
│ ├── resource.py # Resource class with availability management
│ └── init.py
├── views/ # User interface
│ ├── console_ui.py # Menu-driven console interface
│ └── init.py
├── controllers/ # Application logic
│ ├── dispatcher.py # Smart allocation engine
│ ├── main_controller.py
│ └── init.py
├── tests/ # Test suite (87% coverage)
│ ├── unit/ # Component tests
│ ├── integration/ # System workflow tests
│ └── init.py
├── main.py # Application entry
└── README.md


## Core Features
### Intelligent Allocation
- Priority-based dispatching (high > medium > low)
- Automatic reallocation for critical incidents
- Zone-based proximity calculations
- Resource type matching (ambulance/fire/police)

### Incident Management
- CRUD operations with validation
- Dynamic priority adjustment
- Status tracking (unassigned/assigned/resolved)
- Multi-resource requirements support

### Testing Framework
- Unit tests for all components
- Integration tests for full workflows
- Edge case coverage:
  - Resource contention scenarios
  - Priority escalation cases
  - Failure rollback testing

## Usage
```bash
# Run all tests (unit + integration)
python -m unittest discover tests

# Start application
python main.py

# Development workflow
git checkout -b fix/bug-description   # Create branch
python -m unittest tests/test_module.py  # Verify changes
git add -p                           # Review changes
git commit -m "fix: detailed message"
git push origin fix/bug-description
