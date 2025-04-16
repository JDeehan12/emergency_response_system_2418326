# Emergency Response System  
**SDLC Method**: Agile (iterative development in sprints)

## Overview  
This project simulates an Emergency Response System, allowing users to report incidents, assign resources, and manage ongoing emergency operations through a console-based interface.

## Project Structure  
Follows the MVC (Model-View-Controller) architecture:
- `models/` – Data models for incidents and resources  
- `views/` – Console-based user interface  
- `controllers/` – Core logic and interaction between models and views  
- `tests/` – Unit tests covering core components  

## Features  
- Console UI for user interaction  
- Report new incidents with validation  
- Add and assign resources  
- View active incidents and available resources  
- Input validation for incident types, zone numbers, and priorities  
- Unit tests for UI functionality  

## Running Tests  
To run the unit tests:
```bash
python -m unittest discover tests

## Start System Using
python main.py 

Follow the menu to:
1. Report New Incident
2. Add New Resource
3. View Active Incidents
4. View Available Resources
5. Exit

## Phase 1: Project Setup
• MVC folder structure initialised
• Git version control enabled