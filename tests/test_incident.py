# tests/test_incident.py
import unittest
from models.incident import Incident

class TestIncident(unittest.TestCase):
    """
    Test cases for the Incident class functionality.
    Tests include attribute initialisation and method behaviour.
    """
    
    def setUp(self):
        """Creates a test incident before each test case."""
        self.test_incident = Incident(
            incident_type="fire",
            location="Zone 1",
            priority="high",
            required_resources=["fire_engine", "ambulance"]
        )
    
    def test_initial_attributes(self):
        """Verifies attributes are correctly initialised."""
        self.assertEqual(self.test_incident.type, "fire")
        self.assertEqual(self.test_incident.location, "Zone 1")
        self.assertEqual(self.test_incident.priority, "high")
        self.assertEqual(self.test_incident.required_resources, ["fire_engine", "ambulance"])
        self.assertEqual(self.test_incident.status, "unassigned")
    
    def test_priority_update(self):
        """Tests priority can be updated."""
        self.test_incident.update_priority("medium")
        self.assertEqual(self.test_incident.priority, "medium")
    
    def test_status_update(self):
        """Tests status can be updated."""
        self.test_incident.set_status("assigned")
        self.assertEqual(self.test_incident.status, "assigned")
    
    def test_incident_id_generation(self):
        """Tests sequential ID generation."""
        i1 = Incident("fire", "Zone 1", "high", [])
        i2 = Incident("medical", "Zone 2", "medium", [])
        self.assertTrue(i1.id.startswith("INC-"))
        self.assertTrue(i2.id.startswith("INC-"))
        self.assertNotEqual(i1.id, i2.id)

if __name__ == "__main__":
    unittest.main()