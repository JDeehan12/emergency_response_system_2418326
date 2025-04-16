"""
Provides console-based user interface for emergency response system.
Handles all user interactions and input validation.
"""

class ConsoleUI:
    """Handles all console input/output operations for the emergency management system."""

    def __init__(self):
        """Initialises the console interface with default settings."""
        self.valid_incident_types = ["fire", "accident", "crime", "medical"]
        self.valid_priorities = ["high", "medium", "low"]  # Fixed from 'valid_priorities'
        self.min_zone = 1
        self.max_zone = 10

    def display_menu(self) -> str:
        """
        Displays main menu and gets user choice.
        
        Returns:
            str: User's menu selection (1-5)
        """
        print("\nEmergency Response System")
        print("1. Report New Incident")
        print("2. Add New Resource")
        print("3. View Active Incidents")
        print("4. View Available Resources")
        print("5. Exit")
        return input("Enter your choice (1-5): ").strip()

    def clear_screen(self) -> None:
        """Clears console screen using simple newline approach."""
        print("\n" * 100)  # Cross-platform clear method

    def report_incident(self) -> dict:
        """
        Guides user through incident reporting with full validation.
        
        Returns:
            dict: Contains validated incident data with keys:
                - type (str): Incident category
                - location (str): Zone identifier
                - priority (str): Severity level
                - resources (list[str]): Required resources
        """
        print("\n=== Report New Incident ===")
        return {
            'type': self._get_valid_input(
                "Incident type", 
                self.valid_incident_types
            ),
            'location': self._get_zone_input(),
            'priority': self._get_valid_input(
                "Priority level", 
                self.valid_priorities
            ),
            'resources': self._get_resources_input()
        }

    def _get_valid_input(self, prompt: str, options: list[str]) -> str:
        """
        Gets and validates user input against allowed options.
        
        Args:
            prompt (str): Description of expected input
            options (list[str]): Valid response options
            
        Returns:
            str: Validated user selection
        """
        while True:
            user_input = input(f"{prompt} ({'/'.join(options)}): ").lower().strip()
            if user_input in options:
                return user_input
            print(f"Error: Must be one of {options}. Try again.")

    def _get_zone_input(self) -> str:
        """
        Gets and validates zone number input.
        
        Returns:
            str: Formatted zone string (e.g. "Zone 3")
        """
        while True:
            zone = input(f"Zone number ({self.min_zone}-{self.max_zone}): ").strip()
            if (zone.isdigit() and 
                self.min_zone <= int(zone) <= self.max_zone):
                return f"Zone {zone}"
            print(f"Invalid zone. Must be {self.min_zone}-{self.max_zone}.")

    def _get_resources_input(self) -> list[str]:
        """
        Gets and parses required resources input.
        
        Returns:
            list[str]: Cleaned list of resource types
        """
        while True:
            raw_input = input("Required resources (comma-separated, e.g. 'ambulance,fire_engine'): ")
            resources = [r.strip() for r in raw_input.split(',') if r.strip()]
            if resources:
                return resources
            print("Error: Must specify at least one resource.")

    def display_incidents(self, incidents: list) -> None:
        """
        Displays formatted table of active incidents.
        """
        header = "\n=== Active Incidents ==="
        col_header = f"{'ID':<10}{'Type':<15}{'Location':<15}{'Priority':<10}{'Status':<15}"
        separator = "-" * 65
        print(header)
        print(col_header)
        print(separator)
        for incident in incidents:
            print(f"{incident.id[:8]:<10}{incident.type:<15}{incident.location:<15}"
                f"{incident.priority:<10}{incident.status:<15}")

    def display_resources(self, resources: list) -> None:
        """
        Displays formatted table of available resources.
        """
        header = "\n=== Available Resources ==="
        col_header = f"{'Type':<15}{'Location':<15}{'Status':<15}"
        separator = "-" * 45
        print(header)
        print(col_header)
        print(separator)
        for resource in resources:
            status = "Available" if resource.is_available else f"Assigned to {resource.assigned_incident[:8]}"
            print(f"{resource.resource_type:<15}{resource.location:<15}{status:<15}")