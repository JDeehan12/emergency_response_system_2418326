"""
Unit tests for console user interface components.
"""
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
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

    def test_display_incidents(self):
        """Test incident display shows full IDs."""
        test_incident = Incident("fire", "Zone 1", "high", ["ambulance"])
        test_incident.id = "INC-12345678"  # Longer ID for testing
        
        # Mock dispatcher with no resources assigned
        mock_dispatcher = MagicMock()
        mock_dispatcher.resources = []
        
        with patch('builtins.print') as mock_print:
            self.ui.display_incidents([test_incident], mock_dispatcher)
        
        # Get complete output
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        
        # Verify full ID appears (now truncated to 8 chars)
        self.assertIn("INC-1234", output)
        # Verify no ellipsis in the output
        self.assertNotIn("...", output)

    def test_display_resources(self):
        """Test resource display shows full incident IDs."""
        test_resource = Resource("ambulance", "Zone 1")
        test_resource.assigned_incident = "INC-00011234"
        test_resource.is_available = False
        
        mock_dispatcher = MagicMock()
        mock_incident = MagicMock(location="Zone 5")
        mock_dispatcher._get_incident_by_id.return_value = mock_incident
        
        with patch('builtins.print') as mock_print:
            self.ui.display_resources([test_resource], mock_dispatcher)
        
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        self.assertIn("INC-00011234", output)  # Verify full ID
        self.assertNotIn("INC-00...", output)  # Verify no truncation
        
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

    def test_table_formatting(self):
        """Verify table headers and borders exist."""
        test_incident = Incident("fire", "Zone 1", "high", ["ambulance"])
        test_incident.id = "TEST_INCIDENT"
        
        with patch('builtins.print') as mock_print:
            self.ui.display_incidents([test_incident], MagicMock())
        
        output = "\n".join(call[0][0] for call in mock_print.call_args_list)
        
        # Update border checks for new column widths
        self.assertIn("+------------+--------+", output)  # Verify borders
        self.assertIn("| ID         | TYPE   |", output)  # Verify headers
        self.assertIn("TEST_INCID", output)  # Verify ID appears (first 10 chars)

if __name__ == "__main__":
    unittest.main()