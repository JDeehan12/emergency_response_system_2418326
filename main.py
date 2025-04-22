"""
Main entry point for Emergency Response System application.
"""

from controllers.main_controller import MainController

def main():
    """
    Application entry point.
    
    Initialises and runs the main controller.
    """
    try:
        controller = MainController()
        controller.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Critical error: {str(e)}")

if __name__ == "__main__":
    main()