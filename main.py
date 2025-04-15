# main.py
from models.incident import Incident
from views.console_ui import ConsoleUI

def main():
    """
    Entry point for the Emergency Response System application.
    Initialises a test incident and launches the console interface.
    """
    # Test Incident creation (example usage)
    test_incident = Incident(
        incident_type="fire", 
        location="Zone 1", 
        priority="high", 
        required_resources=["fire_engine"]
    )
    print(f"Test incident created: {test_incident.type}")

    # Launch console interface
    console = ConsoleUI()
    console.display_menu()

if __name__ == "__main__":
    main()