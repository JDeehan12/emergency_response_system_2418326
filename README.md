# Emergency Response System  
**SDLC Method**: Agile (iterative development in sprints)  
**Version**: 1.1.0  
**Last Updated**: 2024-04-16

## Overview  
A comprehensive emergency management system that enables efficient allocation of response resources based on incident priority, type, and location through an intuitive console interface.

## Project Structure (MVC Architecture)
emergency_response_system/
├── models/ # Data models and business logic
│ ├── incident.py # Incident class with priority tracking
│ ├── resource.py # Resource class with availability management
│ └── init.py
├── views/ # User interface components
│ ├── console_ui.py # Console-based interaction handler
│ └── init.py
├── controllers/ # Application logic
│ ├── dispatcher.py # Resource allocation engine
│ ├── main_controller.py # Core application flow
│ └── init.py
├── tests/ # Comprehensive test suite
│ ├── test_console_ui.py # UI component tests
│ ├── test_dispatcher.py # Allocation logic tests
│ ├── test_incident.py # Incident model tests
│ ├── test_resource.py # Resource model tests
│ └── init.py
├── main.py # Application entry point
└── README.md # Project documentation

## Key Features
### Incident Management
- Type validation (fire, accident, crime, medical)
- Priority levels (high/medium/low)
- Zone-based location tracking (Zones 1-10)
- Automatic UUID generation

### Resource System
- Menu-driven resource type selection
- Flexible input (numbers/names/aliases):
  - 1/Ambulance/medic
  - 2/Fire Engine/firetruck
  - 3/Police Car/patrol
- Duplicate resource prevention
- Location-based availability tracking

### Core Functionality
- Priority-based resource allocation
- Automatic reallocation for high-priority incidents
- Real-time status updates
- Comprehensive input validation

## Development Workflow
```bash
# Run all unit tests
python -m unittest discover tests

# Start the application
python main.py

# Typical development cycle
git checkout -b feature/feature-name   # Create feature branch
# Implement changes
python -m unittest tests/             # Verify tests
git add .                             # Stage changes
git commit -m "feat: description"     # Commit
git checkout main                     # Switch to main
git merge feature/feature-name        # Merge changes