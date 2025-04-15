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