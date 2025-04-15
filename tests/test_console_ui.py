import unittest
from unittest.mock import patch
from views.console_ui import ConsoleUI

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

if __name__ == "__main__":
    unittest.main()