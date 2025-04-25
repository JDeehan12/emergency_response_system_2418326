"""
Unit tests for console user interface components.
"""
import unittest
from unittest.mock import patch, MagicMock
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

    @patch('builtins.input', side_effect=['3'])  # Mock menu selection
    @patch('builtins.print')
    def test_display_menu_returns_choice(self, mock_print, mock_input):
        """Test menu returns user selection."""
        choice = self.ui.display_menu()
        self.assertEqual(choice, '3')

    @patch('builtins.print')
    def test_clear_screen(self, mock_print):
        """Test screen clearing."""
        self.ui.clear_screen()
        mock_print.assert_called_with("\n" * 100)

    @patch('builtins.input', side_effect=['1', '5', '1', '1', '2', '0'])  # fire, Zone 5, high, ambulance, fire_engine, done
    @patch('builtins.print')
    def test_report_incident(self, mock_print, mock_input):
        """Test complete incident reporting."""
        result = self.ui.report_incident()
        self.assertEqual(result, {
            'type': 'fire',
            'location': 'Zone 5',
            'priority': 'high',
            'resources': ['ambulance', 'fire_engine']
        })

    @patch('builtins.print')
    def test_display_incidents(self, mock_print):
        """Test incident display shows full IDs."""
        test_incident = Incident("fire", "Zone 1", "high", ["ambulance"])
        test_incident.id = "INC-12345678"  # Longer ID for testing
        
        mock_dispatcher = MagicMock()
        mock_dispatcher.resources = []
        
        self.ui.display_incidents([test_incident], mock_dispatcher)
        
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("INC-1234", output)
        self.assertNotIn("...", output)

    @patch('builtins.print')
    def test_display_resources(self, mock_print):
        """Test resource display shows full incident IDs."""
        test_resource = Resource("ambulance", "Zone 1")
        test_resource.assigned_incident = "INC-00011234"
        test_resource.is_available = False
        
        mock_dispatcher = MagicMock()
        mock_incident = MagicMock(location="Zone 5")
        mock_dispatcher._get_incident_by_id.return_value = mock_incident
        
        self.ui.display_resources([test_resource], mock_dispatcher)
        
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("INC-00011234", output)
        self.assertNotIn("INC-00...", output)
        
    @patch('builtins.print')
    def test_menu_with_allocation_option(self, mock_print):
        """Test menu shows allocation option."""
        with patch('builtins.input', return_value=''):  # Mock empty input
            self.ui.display_menu()
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("5. Allocate Resources", output)

    @patch('builtins.input', side_effect=['1', '5', '2', '1', '0'])
    @patch('builtins.print')
    def test_report_incident_with_menus(self, mock_print, mock_input):
        """Test incident reporting with menu selections."""
        result = self.ui.report_incident()
        self.assertEqual(result['type'], 'fire')
        self.assertEqual(result['priority'], 'medium')
        self.assertEqual(result['resources'], ['ambulance'])

    @patch('builtins.print')
    def test_incident_display_with_assignments(self, mock_print):
        """Test incident display shows assigned resources."""
        test_incident = Incident("fire", "Zone 1", "high", ["fire_engine"])
        test_incident.status = "assigned"
        
        test_resource = Resource("fire_engine", "Zone 1")
        test_resource.assign_to_incident(test_incident.id)
        
        dispatcher = Dispatcher()
        dispatcher.incidents.append(test_incident)
        dispatcher.resources.append(test_resource)
        
        self.ui.display_incidents([test_incident], dispatcher)
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("fire_engine", output)

    @patch('builtins.print')
    def test_table_formatting(self, mock_print):
        """Verify table headers and borders exist."""
        test_incident = Incident("fire", "Zone 1", "high", ["ambulance"])
        test_incident.id = "TEST_INCIDENT"
        
        self.ui.display_incidents([test_incident], MagicMock())
        
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("+------------+--------+", output)
        self.assertIn("| ID         | TYPE   |", output)
        self.assertIn("TEST_INCID", output)

if __name__ == "__main__":
    unittest.main()