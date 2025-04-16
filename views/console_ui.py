"""
Provides console-based user interface for emergency response system.
Handles all user interactions and input validation.
"""

from typing import Optional
from controllers.dispatcher import Dispatcher
from models.resource import RESOURCE_TYPES

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
        """Gets resource selection from menu."""
        selected = []
        while True:
            print("\n=== Required Resources ===")
            print("Current selection:", ", ".join(selected) if selected else "None")
            print("0. Done selecting")
            self._display_resource_menu()
            
            choice = input("Add resource (0-3): ").strip()
            if choice == '0':
                if not selected:
                    print("Error: At least one resource required")
                    continue
                return selected
            elif choice.isdigit() and int(choice) in RESOURCE_TYPES:
                resource = RESOURCE_TYPES[int(choice)]["id"]
                if resource not in selected:
                    selected.append(resource)
                else:
                    print(f"{resource} already selected.")
            else:
                print("Invalid selection. Please try again.")

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

    def display_incidents(self, incidents: list, dispatcher: Dispatcher) -> None:
        """Displays incidents with assignment info."""
        print("\n=== Active Incidents ===")
        print(f"{'ID':<8}{'Type':<12}{'Location':<10}{'Priority':<10}{'Status':<12}{'Assigned Resources':<20}")
        print("-" * 72)
        for incident in incidents:
            resources = [r.resource_type for r in dispatcher.resources 
                        if r.assigned_incident == incident.id]
            res_str = ", ".join(resources) if resources else "None"
            print(f"{incident.id:<8}{incident.type:<12}{incident.location:<10}"
                f"{incident.priority:<10}{incident.status:<12}{res_str:<20}")

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