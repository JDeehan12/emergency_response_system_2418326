import unittest
import logging
import time
from controllers.dispatcher import Dispatcher
from models.incident import Incident
from models.resource import Resource
from controllers.main_controller import MainController

class TestDispatcher(unittest.TestCase):
    """Tests for Dispatcher resource allocation logic."""

    def setUp(self):
        self.dispatcher = Dispatcher()
        from models.incident import Incident
        Incident._id_counter = 0
        self.ambulance = Resource("ambulance", "Zone 1")
        self.fire_engine = Resource("fire_engine", "Zone 2")
        self.police_car = Resource("police_car", "Zone 1")
        self.dispatcher.add_resource(self.ambulance)
        self.dispatcher.add_resource(self.fire_engine)
    
    def tearDown(self):
        # Clean up any resources
        self.dispatcher.incidents = []
        self.dispatcher.resources = []

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
    
    def test_high_priority_with_available_resources(self):
        """Verify newly added resources are properly allocated to unassigned incidents."""
        # Clear existing resources
        self.dispatcher.resources = []
        
        # Add initial limited resources
        self.dispatcher.add_resource(Resource("ambulance", "Zone 1"))
        self.dispatcher.add_resource(Resource("fire_engine", "Zone 1"))
        
        # Create incidents - all high priority but with different requirements
        high1 = Incident("medical", "Zone 1", "high", ["ambulance"])
        high2 = Incident("fire", "Zone 2", "high", ["fire_engine"])
        medium = Incident("accident", "Zone 3", "medium", ["ambulance"])
        
        # Add incidents
        self.dispatcher.add_incident(high1)
        self.dispatcher.add_incident(high2)
        self.dispatcher.add_incident(medium)
        
        # First allocation - should assign both high priority incidents
        result = self.dispatcher.allocate_resources()
        self.assertEqual(high1.status, "assigned", "First high-priority should be assigned")
        self.assertEqual(high2.status, "assigned", "Second high-priority should be assigned")
        self.assertEqual(medium.status, "unassigned", "Medium priority should wait")
        
        # Add new resources
        self.dispatcher.add_resource(Resource("ambulance", "Zone 2"))
        self.dispatcher.add_resource(Resource("fire_engine", "Zone 2"))
        
        # Reallocate - should now assign all incidents
        result = self.dispatcher.allocate_resources()
        self.assertEqual(high1.status, "assigned", "First high-priority remains assigned")
        self.assertEqual(high2.status, "assigned", "Second high-priority remains assigned")
        self.assertEqual(medium.status, "assigned", "Medium priority now assigned")

    def test_high_priority_guaranteed_assignment(self):
        """Verify high-priority incidents always get assigned when possible."""
        # Setup with limited resources
        self.dispatcher.resources = [
            Resource("ambulance", "Zone 1"),
            Resource("fire_engine", "Zone 1")
        ]
        
        # Create competing incidents
        high_inc = Incident("fire", "Zone 1", "high", ["ambulance", "fire_engine"])
        low_inc = Incident("accident", "Zone 1", "low", ["ambulance", "fire_engine"])
        
        # Add high priority first
        self.dispatcher.add_incident(high_inc)
        self.assertEqual(high_inc.status, "assigned")
        
        # Add low priority - should remain unassigned
        self.dispatcher.add_incident(low_inc)
        self.assertEqual(low_inc.status, "unassigned")
        
        # Add new resource - should go to high priority if needed
        self.dispatcher.add_resource(Resource("ambulance", "Zone 2"))
        self.dispatcher.allocate_resources()
        self.assertEqual(high_inc.status, "assigned")

    def test_competing_high_priority_incidents(self):
        """Verify multiple high-priority incidents are handled correctly with timestamp-based prioritization."""
        # Setup with limited resources
        self.dispatcher.resources = [
            Resource("ambulance", "Zone 1"),
            Resource("fire_engine", "Zone 1")
        ]
        
        # Create competing high-priority incidents
        high1 = Incident("medical", "Zone 1", "high", ["ambulance", "fire_engine"])
        # Simulate older timestamp by setting it manually
        high1.timestamp = time.time() - 10  # 10 seconds older
        
        high2 = Incident("fire", "Zone 2", "high", ["ambulance", "fire_engine"])
        # high2 will have newer timestamp by default
        
        # Add incidents in reverse order to ensure timestamp is what matters
        self.dispatcher.add_incident(high2)
        self.dispatcher.add_incident(high1)
        
        # First allocation attempt
        self.dispatcher.allocate_resources()
        
        # Verify newer incident is assigned first
        self.assertEqual(high2.status, "assigned",
                        "Newer high-priority incident should be assigned first")
        self.assertEqual(high1.status, "unassigned",
                        "Older high-priority incident should wait when resources are limited")
        
        # Add additional resources
        self.dispatcher.add_resource(Resource("ambulance", "Zone 2"))
        self.dispatcher.add_resource(Resource("fire_engine", "Zone 2"))
        
        # Reallocate
        self.dispatcher.allocate_resources()
        
        # Now both should be assigned
        self.assertEqual(high1.status, "assigned",
                        "Older high-priority should now be assigned with new resources")
        self.assertEqual(high2.status, "assigned",
                        "Newer high-priority should remain assigned")

if __name__ == "__main__":
    unittest.main()