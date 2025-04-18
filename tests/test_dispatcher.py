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
        self.police_car = Resource("police_car", "Zone 1")
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
        self.dispatcher.resources = []
        ambulance = Resource("ambulance", "Zone 1")
        self.dispatcher.add_resource(ambulance)
        
        low = Incident("accident", "Zone 1", "low", ["ambulance"])
        high = Incident("heart attack", "Zone 1", "high", ["ambulance"])
        
        self.dispatcher.add_incident(high)  # Add high priority first
        self.dispatcher.add_incident(low)
        
        self.assertEqual(high.status, "assigned")
        self.assertEqual(ambulance.assigned_incident, high.id)
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
        
        # Verify all resources assigned
        assigned_resources = [r for r in self.dispatcher.resources 
                            if r.assigned_incident == incident.id]
        self.assertEqual(len(assigned_resources), 3)
        
        # Verify allocation log now uses resource IDs
        log_entries = [v for k,v in self.dispatcher.allocation_log.items() 
                    if k.startswith(incident.id)]
        self.assertEqual(len(log_entries), 3)
        def test_assignment_rollback_on_failure(self):
            self.dispatcher.resources = [
                Resource("ambulance", "Zone 1"),
                Resource("fire_engine", "Zone 1")  # Deliberately missing police_car
            ]
            
            incident = Incident("major", "Zone 1", "high", 
                            ["ambulance", "fire_engine", "police_car"])
            self.dispatcher.add_incident(incident)
            
            # Verify rollback occurred
            self.assertEqual(incident.status, "unassigned")
            assigned = [r for r in self.dispatcher.resources if not r.is_available]
            self.assertEqual(len(assigned), 0)

    def test_complex_allocation_scenario(self):
        """Test multiple incidents with shared resource requirements"""
        # Setup resources
        self.dispatcher.resources = [
            Resource("ambulance", "Zone 1"),
            Resource("ambulance", "Zone 2"), 
            Resource("fire_engine", "Zone 1")
        ]
        
        # Create incidents
        incident1 = Incident("accident", "Zone 1", "high", ["ambulance"])
        incident2 = Incident("fire", "Zone 2", "medium", ["fire_engine", "ambulance"])
        
        # Process allocations
        self.dispatcher.add_incident(incident1)
        self.dispatcher.add_incident(incident2)
        
        # Verify results
        self.assertEqual(incident1.status, "assigned")
        self.assertEqual(incident2.status, "assigned")
        
        assigned_resources = [r for r in self.dispatcher.resources if not r.is_available]
        self.assertEqual(len(assigned_resources), 3)  # All resources should be assigned

    def test_duplicate_resources_allowed(self):
        """Verify multiple resources can exist at same location."""
        # Clear existing test resources first
        self.dispatcher.resources = []
        
        self.dispatcher.add_resource(Resource("ambulance", "Zone 1"))
        self.dispatcher.add_resource(Resource("ambulance", "Zone 1"))
        self.assertEqual(len([r for r in self.dispatcher.resources 
                            if r.resource_type == "ambulance" and r.location == "Zone 1"]), 2)

if __name__ == "__main__":
    unittest.main()