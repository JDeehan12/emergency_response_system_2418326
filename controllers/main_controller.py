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
        """Initialises application components."""
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
                self.ui.display_incidents(self.dispatcher.incidents, self.dispatcher)
            elif choice == '4':  # View resources
                self.ui.display_resources(self.dispatcher.resources, self.dispatcher)
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
        """Handles resource addition without duplicate checking."""
        try:
            data = self.ui.get_resource_input()                
            resource = Resource(data['type'], data['location'])
            self.dispatcher.add_resource(resource)
            print(f"[SUCCESS] Added {data['type']} at {data['location']}")
            
        except ValueError as e:
            print(f"[ERROR] {str(e)}")

    def _handle_allocation(self):
        """Handles manual resource allocation with proper status updates"""
        print("\n=== Performing Smart Allocation ===")
        print("1. Checking all high-priority incidents")
        print("2. Reallocating resources where needed")
        print("3. Verifying assignments...\n")
        
        result = self.dispatcher.allocate_resources()
        
        # Detailed reporting
        assigned = [i for i in self.dispatcher.incidents if i.status == 'assigned']
        unassigned = [i for i in self.dispatcher.incidents if i.status == 'unassigned']
        
        print("\n=== Allocation Report ===")
        print(f"Successfully assigned: {len(assigned)} incidents")
        if unassigned:
            print(f"Needs attention:")
            for incident in unassigned:
                required = ", ".join(incident.required_resources)
                print(f" - {incident.id} ({incident.type} in {incident.location}) needs: {required}")