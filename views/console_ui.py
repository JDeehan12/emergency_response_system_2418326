"""
Provides console-based user interface for emergency response system.
"""

class ConsoleUI:
    """Handles all console input/output operations."""
    
    def display_menu(self) -> str:
        """
        Displays main menu and gets user choice.
        
        Returns:
            User's menu selection as string
        """
        print("\nEmergency Response System")
        print("1. Report New Incident")
        print("2. Add New Resource")
        print("3. View Active Incidents") 
        print("4. View Available Resources")
        print("5. Exit")
        return input("Enter your choice (1-5): ")

    def clear_screen(self):
        """Clears console screen."""
        print("\n" * 100)  # Simple clear for cross-platform

    def report_incident(self) -> dict:
        """
        Guides user through incident reporting.
        
        Returns:
            Dictionary of incident data:
            {
                'type': str,
                'location': str, 
                'priority': str,
                'resources': list[str]
            }
        """
        print("\nReport New Incident")
        return {
            'type': self._get_valid_input("Incident type", ["fire", "accident", "crime"]),
            'location': self._get_zone_input(),
            'priority': self._get_valid_input("Priority", ["high", "medium", "low"]),
            'resources': self._get_resources_input()
        }

    def _get_valid_input(self, prompt: str, options: list) -> str:
        """Gets validated user input from limited options."""
        while True:
            value = input(f"{prompt} ({'/'.join(options)}): ").lower()
            if value in options:
                return value
            print(f"Invalid input. Please choose from {options}")

    def _get_zone_input(self) -> str:
        """Gets and validates zone input."""
        while True:
            zone = input("Zone (1-10): ")
            if zone.isdigit() and 1 <= int(zone) <= 10:
                return f"Zone {zone}"
            print("Invalid zone. Please enter 1-10")
    