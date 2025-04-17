import unittest
from controllers.dispatcher import Dispatcher
from models.incident import Incident
from models.resource import Resource
from controllers.main_controller import MainController

class TestDispatcher(unittest.TestCase):
    """Tests for Dispatcher resource allocation logic."""

    def setUp(self):
        self.dispatcher = Dispatcher()
        self.ambulance = Resource("ambulance", "Zone 1")
        self.fire_engine = Resource("fire_engine", "Zone 2")
        self.dispatcher.add_resource(self.ambulance)
        self.dispatcher.add_resource(self.fire_engine)

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

    def test_priority_allocation(self):
        """Verify high-priority incidents get resources first."""
        # Clear existing resources from setUp
        self.dispatcher.resources = []
        
        # Add exactly one ambulance
        ambulance = Resource("ambulance", "Zone 1")
        self.dispatcher.add_resource(ambulance)
        
        # Create incidents
        low = Incident("accident", "Zone 1", "low", ["ambulance"])
        high = Incident("heart attack", "Zone 1", "high", ["ambulance"])
        
        # Add high priority last to test prioritization
        self.dispatcher.add_incident(low)
        self.dispatcher.add_incident(high)
        
        # Verify high priority got the resource
        self.assertEqual(high.status, "assigned")
        self.assertEqual(ambulance.assigned_incident, high.id)
        
        # Verify low priority remains unassigned
        self.assertEqual(low.status, "unassigned")

    def test_reallocation(self):
        """Verify resources get reallocated to high priority."""
        # Clear existing resources from setUp
        self.dispatcher.resources = []
        
        # Add exactly one ambulance
        ambulance = Resource("ambulance", "Zone 1")
        self.dispatcher.add_resource(ambulance)
        
        # Create and add low priority incident
        low = Incident("accident", "Zone 1", "low", ["ambulance"])
        self.dispatcher.add_incident(low)
        
        # Verify initial assignment
        self.assertEqual(low.status, "assigned")
        self.assertEqual(ambulance.assigned_incident, low.id)
        
        # Trigger high priority incident
        high = Incident("heart attack", "Zone 1", "high", ["ambulance"])
        self.dispatcher.add_incident(high)
        
        # Verify reallocation occurred
        self.assertEqual(high.status, "assigned")
        self.assertEqual(ambulance.assigned_incident, high.id)
        self.assertEqual(low.status, "unassigned")
    
    def test_manual_allocation(self):
        """Test manual allocation triggering."""
        # Add a test resource first
        test_resource = Resource("fire_engine", "Zone 1")
        self.dispatcher.add_resource(test_resource)
        
        # Add and test incident
        test_incident = Incident("fire", "Zone 1", "high", ["fire_engine"])
        self.dispatcher.add_incident(test_incident)
        
        result = self.dispatcher.allocate_resources()
        self.assertIn('assigned', result)
        self.assertIn('unassigned', result)
        self.assertEqual(len(result['assigned']), 1)

    def test_default_resources_loading(self):
        """Test default resources are loaded."""
        controller = MainController()
        self.assertEqual(len(controller.dispatcher.resources), 6)

    def test_multiple_resource_assignment(self):
        """Test incident can be assigned multiple resources."""
        self.dispatcher.resources = [
            Resource("ambulance", "Zone 1"),
            Resource("fire_engine", "Zone 1"),
            Resource("police_car", "Zone 1")
        ]
        
        incident = Incident("major", "Zone 1", "high", 
                        ["ambulance", "fire_engine", "police_car"])
        self.dispatcher.add_incident(incident)
        
        assigned_resources = [r for r in self.dispatcher.resources 
                            if r.assigned_incident == incident.id]
        self.assertEqual(len(assigned_resources), 3)
        # Verify allocation log
        self.assertEqual(len(self.dispatcher.allocation_log), 3)

if __name__ == "__main__":
    unittest.main()