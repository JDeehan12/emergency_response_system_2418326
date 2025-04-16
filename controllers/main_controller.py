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
        self._load_default_resources()

    def _load_default_resources(self):
        """Preloads default resources."""
        defaults = [
            ("ambulance", "Zone 1"), ("ambulance", "Zone 2"),
            ("fire_engine", "Zone 1"), ("fire_engine", "Zone 2"),
            ("police_car", "Zone 1"), ("police_car", "Zone 2")
        ]
        for r_type, location in defaults:
            self.dispatcher.add_resource(Resource(r_type, location))
        
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
            elif choice == '5':  # Allocate resources
                result = self.dispatcher.allocate_resources()
                print(f"\nAllocation completed:")
                print(f"- Assigned: {len(result['assigned'])} incidents")
                print(f"- Unassigned: {len(result['unassigned'])} incidents")
            elif choice == '6':  # Exit
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

    def _handle_add_resource(self):
        """Handles complete resource addition workflow with duplicate checking."""
        try:
            data = self.ui.get_resource_input()
            
            # Check for existing identical resource
            if any(r.resource_type == data['type'] and 
                r.location == data['location']
                for r in self.dispatcher.resources):
                raise ValueError(f"Resource {data['type']} already exists at {data['location']}")
                
            resource = Resource(data['type'], data['location'])
            self.dispatcher.add_resource(resource)
            print(f"[SUCCESS] Added {data['type']} at {data['location']}")
            
        except ValueError as e:
            print(f"[ERROR] {str(e)}")