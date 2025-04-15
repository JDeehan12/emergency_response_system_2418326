import unittest
from controllers.dispatcher import Dispatcher
from models.incident import Incident
from models.resource import Resource

class TestDispatcher(unittest.TestCase):
    """Tests for Dispatcher resource allocation logic."""

    def setUp(self):
        self.dispatcher = Dispatcher()
        self.ambulance = Resource("ambulance", "Zone 1")
        self.fire_engine = Resource("fire_engine", "Zone 2")
        self.dispatcher.add_resource(self.ambulance)
        self.dispatcher.add_resource(self.fire_engine)

    def test_priority_allocation(self):
        """High-priority incidents get resources first when scarce."""
        high_pri = Incident("fire", "Zone 1", "high", ["ambulance"])
        low_pri = Incident("accident", "Zone 1", "low", ["ambulance"])
        
        # Add low priority first
        self.dispatcher.add_incident(low_pri)
        self.dispatcher.add_incident(high_pri)
        
        # Verify high-priority got the resource
        self.assertEqual(high_pri.status, "assigned")
        self.assertEqual(low_pri.status, "unassigned")
        self.assertEqual(self.ambulance.assigned_incident, high_pri.id)

    def test_proximity_matching(self):
        """Resources are allocated from same zone when possible."""
        incident = Incident("fire", "Zone 2", "medium", ["fire_engine"])
        self.dispatcher.add_incident(incident)
        self.assertEqual(self.fire_engine.assigned_incident, incident.id)

    def test_multiple_resource_types(self):
        """Incidents requiring different resources both get assigned."""
        medical = Incident("heart attack", "Zone 1", "high", ["ambulance"])
        fire = Incident("fire", "Zone 2", "high", ["fire_engine"])
        
        self.dispatcher.add_incident(medical)
        self.dispatcher.add_incident(fire)
        
        self.assertEqual(medical.status, "assigned")
        self.assertEqual(fire.status, "assigned")

    def test_reallocation(self):
        """Resources are taken from low-priority for high-priority."""
        low_pri = Incident("accident", "Zone 1", "low", ["ambulance"])
        self.dispatcher.add_incident(low_pri)
        
        high_pri = Incident("fire", "Zone 1", "high", ["ambulance"])
        self.dispatcher.add_incident(high_pri)
        
        self.assertEqual(high_pri.status, "assigned")
        self.assertEqual(low_pri.status, "unassigned")

if __name__ == "__main__":
    unittest.main()