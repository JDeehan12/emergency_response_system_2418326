"""
Unit tests for console user interface components.
"""
import unittest
from unittest.mock import patch
from views.console_ui import ConsoleUI
from models.incident import Incident
from models.resource import Resource

class TestConsoleUI(unittest.TestCase):
    """Tests console user interface components."""
    
    def setUp(self):
        self.ui = ConsoleUI()
    
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

    @patch('builtins.input', side_effect=['fire', '5', 'high', 'ambulance,police'])
    def test_report_incident(self, mock_input):
        """Test complete incident reporting."""
        result = self.ui.report_incident()
        self.assertEqual(result, {
            'type': 'fire',
            'location': 'Zone 5',
            'priority': 'high',
            'resources': ['ambulance', 'police']
        })

    @patch('builtins.print')
    def test_display_incidents(self, mock_print):
        """Test incident display formatting."""
        test_incident = Incident("fire", "Zone 1", "high", ["ambulance"])
        test_incident.id = "test1234"
        test_incident.status = "unassigned"
        
        self.ui.display_incidents([test_incident])
        
        # Get all printed lines
        printed_lines = [call[0][0] for call in mock_print.call_args_list]
        
        # Verify the data line exists in output
        expected_line = "test1234  fire           Zone 1         high      unassigned     "
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
        controller = MainController()
        
        # Mock user input for first resource
        with patch('views.console_ui.ConsoleUI.get_resource_input', 
                return_value={'type': 'ambulance', 'location': 'Zone 1'}):
            controller._handle_add_resource()
        
        # Attempt to add duplicate
        with patch('views.console_ui.ConsoleUI.get_resource_input',
                return_value={'type': 'ambulance', 'location': 'Zone 1'}):
            with patch('builtins.print') as mock_print:
                controller._handle_add_resource()
                
                # Verify error message
                error_msg = next(call_args[0][0] 
                            for call_args in mock_print.call_args_list
                            if '[ERROR]' in call_args[0][0])
                self.assertIn("already exists", error_msg)
        
        # Verify only one resource was added
        self.assertEqual(len(controller.dispatcher.resources), 1)

if __name__ == "__main__":
    unittest.main()