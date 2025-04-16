"""
Unit tests for console user interface components.
"""
import unittest
from unittest.mock import patch
from views.console_ui import ConsoleUI
from models.incident import Incident
from models.resource import Resource
from controllers.main_controller import MainController
from controllers.dispatcher import Dispatcher

class TestConsoleUI(unittest.TestCase):
    """Tests console user interface components."""
    
    def setUp(self):
        self.ui = ConsoleUI()
        self.dispatcher = Dispatcher()
        self.test_incident = Incident("fire", "Zone 1", "high", ["ambulance"])
        self.test_resource = Resource("ambulance", "Zone 1")
    
    @patch('builtins.input', return_value='3')
    def test_display_menu_returns_choice(self, mock_input):
        """Test menu returns user selection."""
        choice = self.ui.display_menu()
        self.assertEqual(choice, '3')
    
    @patch('builtins.print')
    def test_clear_screen(self, mock_print):
        """Test screen clearing."""
        self.ui.clear_screen()
        mock_print.assert_called_with("\n" * 100)

    @patch('builtins.input', side_effect=['1', '5', '1', '1', '2', '0'])  # fire, Zone 5, high, ambulance, police, done
    def test_report_incident(self, mock_input):
        """Test complete incident reporting."""
        result = self.ui.report_incident()  #This line was missing
        self.assertEqual(result, {
            'type': 'fire',
            'location': 'Zone 5',
            'priority': 'high',
            'resources': ['ambulance', 'fire_engine']
        })

    @patch('builtins.print')
    def test_display_incidents(self, mock_print):
        """Test incident display formatting."""
        test_incident = Incident("fire", "Zone 1", "high", ["ambulance"])
        test_incident.id = "test1234"
        test_incident.status = "unassigned"
        
        # Create a dispatcher and pass it to the method
        dispatcher = Dispatcher()
        self.ui.display_incidents([test_incident], dispatcher)
        
        # Get all printed lines
        printed_lines = [call[0][0] for call in mock_print.call_args_list]
        
        # Verify the data line exists in output
        expected_line = "test1234fire        Zone 1    high      unassigned  None                "
        self.assertIn(expected_line, printed_lines)

    @patch('builtins.print')
    def test_display_resources(self, mock_print):
        """Test resource display formatting."""
        test_resource = Resource("ambulance", "Zone 1")
        test_resource.assigned_incident = "incident_5678"
        test_resource.is_available = False
        
        self.ui.display_resources([test_resource])
        
        # Get all printed lines
        printed_lines = [call[0][0] for call in mock_print.call_args_list]
        
        # Verify the data line exists in output
        expected_line = "ambulance      Zone 1         Assigned to incident"
        self.assertIn(expected_line, printed_lines)

    def test_duplicate_resource_prevention(self):
        """Verify system prevents adding duplicate resources."""
        # Initialize with empty dispatcher
        controller = MainController()
        controller.dispatcher.resources = []  # Ensure clean state
        
        # Mock resource input
        test_resource = {'type': 'ambulance', 'location': 'Zone 1'}
        
        # First addition (should succeed)
        with patch('views.console_ui.ConsoleUI.get_resource_input', 
                return_value=test_resource):
            with patch('builtins.print') as mock_print:
                controller._handle_add_resource()
                success_msgs = [args[0] for args, _ in mock_print.call_args_list]
                self.assertTrue(any("[SUCCESS]" in msg for msg in success_msgs))
        
        # Attempt duplicate (should fail)
        with patch('views.console_ui.ConsoleUI.get_resource_input',
                return_value=test_resource):
            with patch('builtins.print') as mock_print:
                controller._handle_add_resource()
                error_msgs = [args[0] for args, _ in mock_print.call_args_list]
                self.assertTrue(any("[ERROR]" in msg for msg in error_msgs))
                self.assertTrue(any("already exists" in msg for msg in error_msgs))
        
        # Verify only one resource was added
        self.assertEqual(len(controller.dispatcher.resources), 1)
    
    def test_menu_with_allocation_option(self):
        """Test menu shows allocation option."""
        with patch('builtins.print') as mock_print:
            self.ui.display_menu()
            output = "\n".join(call[0][0] for call in mock_print.call_args_list)
            self.assertIn("5. Allocate Resources", output)

    @patch('builtins.input', side_effect=['1', '5', '2', '1', '0'])
    def test_report_incident_with_menus(self, mock_input):
        """Test incident reporting with menu selections."""
        result = self.ui.report_incident()
        self.assertEqual(result['type'], 'fire')
        self.assertEqual(result['priority'], 'medium')
        self.assertEqual(result['resources'], ['ambulance'])

    def test_incident_display_with_assignments(self):
        """Test incident display shows assigned resources."""
        # Create test incident
        test_incident = Incident("fire", "Zone 1", "high", ["fire_engine"])
        test_incident.status = "assigned"
        
        # Create test resource and assign it
        test_resource = Resource("fire_engine", "Zone 1")
        test_resource.assign_to_incident(test_incident.id)
        
        # Create dispatcher and add both
        dispatcher = Dispatcher()
        dispatcher.incidents.append(test_incident)
        dispatcher.resources.append(test_resource)
        
        with patch('builtins.print') as mock_print:
            self.ui.display_incidents([test_incident], dispatcher)
            output = "\n".join(call[0][0] for call in mock_print.call_args_list)
            self.assertIn("fire_engine", output)

if __name__ == "__main__":
    unittest.main()