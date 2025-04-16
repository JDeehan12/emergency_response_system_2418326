"""
Tests for resource type system and input handling.
"""

import unittest
from unittest.mock import patch
from models.resource import Resource, RESOURCE_TYPES
from views.console_ui import ConsoleUI

class TestResourceSystem(unittest.TestCase):
    
    def test_resource_type_validation(self):
        """Test valid and invalid resource types."""
        # Valid type
        Resource("ambulance", "Zone 1")
        # Invalid type
        with self.assertRaises(ValueError):
            Resource("invalid_type", "Zone 1")

    def test_resource_type_definitions(self):
        """Verify all resource types have required fields."""
        for rtype in RESOURCE_TYPES.values():
            self.assertIn("id", rtype)
            self.assertIn("name", rtype)
            self.assertIn("aliases", rtype)

class TestConsoleUIResourceInput(unittest.TestCase):
    
    def setUp(self):
        self.ui = ConsoleUI()
    
    @patch('builtins.input', return_value='2')
    def test_numeric_resource_selection(self, mock_input):
        """Test numeric menu selection."""
        result = self.ui._get_resource_choice()
        self.assertEqual(result, "fire_engine")
    
    @patch('builtins.input', return_value='firetruck')
    def test_alias_resource_selection(self, mock_input):
        """Test text alias matching."""
        result = self.ui._get_resource_choice()
        self.assertEqual(result, "fire_engine")
    
    @patch('builtins.print')
    @patch('views.console_ui.ConsoleUI._get_zone_input', return_value="Zone 3")
    @patch('views.console_ui.ConsoleUI._get_resource_choice', return_value="police_car")
    def test_complete_resource_input(self, mock_choice, mock_zone, mock_print):
        """Test full resource input flow."""
        result = self.ui.get_resource_input()
        self.assertEqual(result, {
            'type': 'police_car',
            'location': 'Zone 3'
        })