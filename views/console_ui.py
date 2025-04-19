"""
Provides console-based user interface for emergency response system.
Handles all user interactions and input validation.
"""

from typing import Optional
from controllers.dispatcher import Dispatcher
from models.resource import RESOURCE_TYPES
from tabulate import tabulate

class ConsoleUI:
    """Handles all console input/output operations for the emergency management system."""

    def __init__(self):
        """Initialises the console interface with default settings."""
        self.valid_incident_types = ["fire", "accident", "crime", "medical"]
        self.valid_priorities = ["high", "medium", "low"]  # Fixed from 'valid_priorities'
        self.min_zone = 1
        self.max_zone = 10
        self.table_style = "grid"  # Options: grid, fancy_grid, psql, simple
        self.table_alignment = "center"

    def display_menu(self) -> str:
        """
        Displays main menu and gets user choice.
        
        Returns:
            str: User's menu selection (1-5)
        """
        print("\n=== Emergency Response System ===")
        print("1. Report New Incident")
        print("2. Add New Resource")
        print("3. View Active Incidents")
        print("4. View Available Resources")
        print("5. Allocate Resources")  # New option
        print("6. Exit")
        return input("Enter your choice (1-6): ").strip()
    
    def _display_options(self, title: str, options: list) -> None:
        """Displays numbered options with title."""
        print(f"\n=== {title} ===")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

    def clear_screen(self) -> None:
        """Clears console screen using simple newline approach."""
        print("\n" * 100)  # Cross-platform clear method

    def report_incident(self) -> dict:
        """Guides user through incident reporting."""
        print("\n=== Report New Incident ===")
        return {
            'type': self._select_from_options("Incident Type", self.valid_incident_types),
            'location': self._get_zone_input(),
            'priority': self._select_from_options("Priority Level", self.valid_priorities),
            'resources': self._select_resources()
        }

    def _select_from_options(self, title: str, options: list) -> str:
        """Gets user selection from numbered options."""
        self._display_options(title, options)
        while True:
            choice = input(f"Select {title.lower()} (1-{len(options)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice)-1]
            print(f"Invalid selection. Please enter 1-{len(options)}")

    def _select_resources(self) -> list:
        """
        Gets resource selection from user through console prompts.
        Implements toggle functionality for adding/removing resources.
        
        Returns:
            list: Sorted list of unique resource types selected
        """
        selected = []
        while True:
            print("\n=== Required Resources ===")
            print("Current selection:", ", ".join(selected) if selected else "None")
            print("0. Done | 1. Ambulance | 2. Fire Engine | 3. Police Car")
            print("(Select number again to toggle resource)")
            
            choice = input("Add/Remove resource (0-3): ").strip()
            
            # Validate input against allowed options
            if choice not in ('0', '1', '2', '3'):
                print("Invalid input. Please enter 0-3")
                continue
                
            # Handle completion request
            if choice == '0':
                if not selected:
                    print("Error: At least one resource required")
                    continue
                return sorted(selected)  # Return alphabetically sorted list
                
            # Toggle resource selection
            resource = RESOURCE_TYPES[int(choice)]["id"]
            if resource in selected:
                selected.remove(resource)
            else:
                # Ensure no duplicate resource types
                if resource not in selected:
                    selected.append(resource)
                else:
                    print(f"Note: {resource} already in selection")

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

    def _format_table(self, headers: list, rows: list) -> str:
        """Standardised table formatting helper."""
        return tabulate(rows, 
                    headers=headers, 
                    tablefmt="grid",  # Changed to standard grid
                    stralign="center",
                    numalign="center")

    def display_incidents(self, incidents: list, dispatcher: Dispatcher) -> None:
        """Displays incidents in standardized table format."""
        headers = ["ID", "TYPE", "LOCATION", "PRIORITY", "STATUS", "RESOURCES"]
        
        # Define column widths (ID shows first 10 characters)
        col_widths = [10, 8, 12, 10, 10, 20]
        
        rows = []
        for incident in incidents:
            resources = ", ".join(set(
                r.resource_type for r in dispatcher.resources 
                if r.assigned_incident == incident.id
            )) or "None"
            
            rows.append([
                incident.id[:col_widths[0]].ljust(col_widths[0]),  # First 10 chars, left-aligned
                incident.type.upper().center(col_widths[1]),
                incident.location.center(col_widths[2]),
                incident.priority.upper().center(col_widths[3]),
                incident.status.upper().center(col_widths[4]),
                resources.center(col_widths[5])
            ])
        
        print("\n" + tabulate(rows, headers=headers, tablefmt="grid"))

    def display_resources(self, resources: list, dispatcher: Dispatcher = None) -> None:
        """Displays resources in standardized table format."""
        headers = ["RESOURCE TYPE", "CURRENT LOCATION", "STATUS"]
        
        # Define column widths
        col_widths = [15, 20, 25]  # Wider columns for better readability
        
        rows = []
        for resource in resources:
            location = resource.location
            if not resource.is_available and dispatcher:
                try:
                    incident = dispatcher._get_incident_by_id(resource.assigned_incident)
                    location = f"{incident.location} (assigned)"
                except Exception:
                    pass
                    
            status = "AVAILABLE" if resource.is_available else f"ASSIGNED TO {resource.assigned_incident}"
            
            rows.append([
                resource.resource_type.upper().ljust(col_widths[0]),
                location.center(col_widths[1]),
                status.center(col_widths[2])
            ])
        
        print("\n" + tabulate(rows, headers=headers, tablefmt="grid"))
        
    def _display_resource_menu(self) -> None:
        """Displays numbered resource type options."""
        print("\nAvailable Resource Types:")
        for num, rtype in RESOURCE_TYPES.items():
            print(f"{num}. {rtype['name']}")

    def _get_resource_choice(self) -> str:
        """
        Gets validated resource type selection.
        
        Returns:
            str: The resource type ID
        """
        while True:
            self._display_resource_menu()
            choice = input("Select resource type (number): ").strip()
            
            if choice.isdigit() and int(choice) in RESOURCE_TYPES:
                return RESOURCE_TYPES[int(choice)]["id"]
                
            # Try to match by name/alias
            matched_type = self._match_resource_input(choice)
            if matched_type:
                return matched_type
                
            print(f"Invalid selection. Please choose 1-{len(RESOURCE_TYPES)} or type a resource name.")

    def _match_resource_input(self, user_input: str) -> Optional[str]:
        """
        Flexible resource type matching.
        
        Args:
            user_input: Raw user input
            
        Returns:
            str: Matched resource ID or None
        """
        user_input = user_input.lower()
        for rtype in RESOURCE_TYPES.values():
            if (user_input == rtype["id"] or 
                user_input == rtype["name"].lower() or
                any(user_input == alias for alias in rtype["aliases"])):
                return rtype["id"]
        return None

    def get_resource_input(self) -> dict:
        """
        Gets complete resource details through guided prompts.
        
        Returns:
            dict: {'type': str, 'location': str}
        """
        print("\n=== Add New Resource ===")
        return {
            'type': self._get_resource_choice(),
            'location': self._get_zone_input()
        }