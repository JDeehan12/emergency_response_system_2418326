"""
Coordinates between UI and dispatcher systems.
Manages the main application workflow.
"""

from views.console_ui import ConsoleUI
from controllers.dispatcher import Dispatcher
from models.incident import Incident
from models.resource import Resource

class MainController:
    """Main application controller handling core workflow."""
    
    def __init__(self):
        """Initialize application components."""
        self.ui = ConsoleUI()
        self.dispatcher = Dispatcher()
        
    def run(self) -> None:
        """Main application loop handling user choices."""
        while True:
            choice = self.ui.display_menu()
            
            if choice == '1':  # Report incident
                self._handle_incident_report()
            elif choice == '2':  # Add resource
                self._handle_add_resource()
            elif choice == '3':  # View incidents
                self.ui.display_incidents(self.dispatcher.incidents)
            elif choice == '4':  # View resources
                self.ui.display_resources(self.dispatcher.resources)
            elif choice == '5':  # Exit
                print("Exiting system...")
                break
            else:
                print("Invalid choice. Please try again.")

    def _handle_incident_report(self) -> None:
        """Handles complete incident reporting workflow."""
        data = self.ui.report_incident()
        incident = Incident(
            data['type'],
            data['location'],
            data['priority'],
            data['resources']
        )
        self.dispatcher.add_incident(incident)
        print(f"Incident {incident.id[:8]} reported successfully.")

    def _handle_add_resource(self) -> None:
        """Handles resource addition workflow."""
        print("\n=== Add New Resource ===")
        resource_type = input("Resource type: ")
        location = input("Location (Zone): ")
        resource = Resource(resource_type, location)
        self.dispatcher.add_resource(resource)
        print(f"{resource_type} at {location} added to available resources.")