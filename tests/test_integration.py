"""
End-to-end integration test for emergency response system.
Tests complete workflow from incident creation to resolution.
"""
import unittest
import time
from controllers.main_controller import MainController
from models.incident import Incident
from models.resource import Resource

class TestSystemIntegration(unittest.TestCase):
    """Tests the complete system workflow"""
    
    def setUp(self):
        """Initialises fresh controller for each test"""
        self.controller = MainController()
        # Clear all state
        self.controller.dispatcher.incidents = []
        self.controller.dispatcher.resources = []
        self.controller.dispatcher.allocation_log = {}
        # Reset incident counter
        from models.incident import Incident
        Incident._id_counter = 0
        
    def test_complete_incident_lifecycle(self):
        """Tests full incident lifecycle from creation to resolution"""
        print("\n=== Starting Test: Complete Incident Lifecycle ===")
        
        # 1. Add test resources
        resources = [
            Resource("ambulance", "Zone 1"),
            Resource("fire_engine", "Zone 2"),  # Only one fire engine available
            Resource("police_car", "Zone 3")
        ]
        for r in resources:
            self.controller.dispatcher.add_resource(r)
        
        # 2. Report first high-priority incident (older timestamp)
        incident1 = Incident(
            incident_type="fire",
            location="Zone 2",
            priority="high",
            required_resources=["fire_engine"]
        )
        incident1.timestamp = time.time() - 10  # Make it older
        self.controller.dispatcher.add_incident(incident1)
        
        # 3. Verify first assignment
        self.assertEqual(incident1.status, "assigned")
        
        # 4. Report newer high-priority incident that needs same resource
        incident2 = Incident(
            incident_type="explosion",
            location="Zone 1",
            priority="high",
            required_resources=["fire_engine"]
        )
        self.controller.dispatcher.add_incident(incident2)
        
        # 5. Verify newer incident took the resource
        self.assertEqual(incident2.status, "assigned",
                        "Newer high-priority incident should get the resource")
        self.assertEqual(incident1.status, "unassigned",
                        "Older high-priority incident should lose the resource")
        
        # 6. Verify the fire engine is assigned to the newer incident
        fire_engine = next(r for r in self.controller.dispatcher.resources 
                        if r.resource_type == "fire_engine")
        self.assertEqual(fire_engine.assigned_incident, incident2.id,
                        "Fire engine should be assigned to newer incident")
        
        print("\n=== Test Completed Successfully ===")

    def test_priority_escalation_reallocation(self):
        """Tests if high priority incident pre-empts a medium priority one"""
        print("\n=== Starting Test: Priority Escalation Reallocation ===")

        # 1. Add test resources
        resources = [
            Resource("ambulance", "Zone 1"),
            Resource("fire_engine", "Zone 1")
        ]
        for r in resources:
            self.controller.dispatcher.add_resource(r)

        # 2. Report a medium-priority incident
        medium_incident = Incident(
            incident_type="chemical_spill",
            location="Zone 1",
            priority="medium",
            required_resources=["ambulance", "fire_engine"]
        )
        self.controller.dispatcher.add_incident(medium_incident)

        # Confirm it's been assigned
        self.assertEqual(medium_incident.status, "assigned")
        assigned = [r for r in self.controller.dispatcher.resources if r.assigned_incident == medium_incident.id]
        self.assertEqual(len(assigned), 2, "Both resources should be assigned to medium-priority incident initially")

        # 3. Report a high-priority incident in same zone needing same resources
        high_incident = Incident(
            incident_type="building_collapse",
            location="Zone 1",
            priority="high",
            required_resources=["ambulance", "fire_engine"]
        )
        self.controller.dispatcher.add_incident(high_incident)

        # Verify reallocation
        print("\nAfter High Priority Incident:")
        for r in sorted(self.controller.dispatcher.resources, key=lambda x: x.resource_type):
            status = "Available" if r.is_available else f"Assigned to {r.assigned_incident}"
            print(f"{r.resource_type}: {status}")

        # Check statuses
        self.assertEqual(high_incident.status, "assigned", "High-priority incident should be assigned")
        self.assertEqual(medium_incident.status, "unassigned", "Medium-priority incident should be unassigned")

        reassigned = [r for r in self.controller.dispatcher.resources if r.assigned_incident == high_incident.id]
        self.assertEqual(len(reassigned), 2, "Resources should be reassigned to high-priority incident")

        # Confirm original incident is no longer using any resources
        for r in self.controller.dispatcher.resources:
            self.assertNotEqual(r.assigned_incident, medium_incident.id,
                                f"{r.resource_type} is still incorrectly assigned to the medium-priority incident")

        print("\n=== Test Completed Successfully ===")

                
if __name__ == "__main__":
    unittest.main()