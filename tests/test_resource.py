import unittest
from models.resource import Resource

class TestResource(unittest.TestCase):
    """
    Unit tests for the Resource class functionality.
    Verifies initialisation, availability toggling, and incident assignment.
    """

    def setUp(self):
        """Create a test resource before each test case."""
        self.test_resource = Resource("ambulance", "Zone 2")

    def test_initial_state(self):
        """Verify resource initialises with correct defaults."""
        self.assertEqual(self.test_resource.resource_type, "ambulance")
        self.assertEqual(self.test_resource.location, "Zone 2")
        self.assertTrue(self.test_resource.is_available)
        self.assertIsNone(self.test_resource.assigned_incident)

    def test_toggle_availability(self):
        """Test availability status can be updated."""
        self.test_resource.toggle_availability(False)
        self.assertFalse(self.test_resource.is_available)

    def test_incident_assignment(self):
        """Test resource can be assigned to an incident."""
        self.test_resource.assign_to_incident("incident_123")
        self.assertEqual(self.test_resource.assigned_incident, "incident_123")
        self.assertFalse(self.test_resource.is_available)

    def test_double_assignment_raises_error(self):
        """Test assigning an already-allocated resource raises an error."""
        self.test_resource.assign_to_incident("incident_123")
        with self.assertRaises(ValueError):
            self.test_resource.assign_to_incident("incident_456")

if __name__ == "__main__":
    unittest.main()