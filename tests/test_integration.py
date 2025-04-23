"""
End-to-end integration test for emergency response system.
Tests complete workflow from incident creation to resolution.
"""
import unittest
from controllers.main_controller import MainController
from models.incident import Incident
from models.resource import Resource

class TestSystemIntegration(unittest.TestCase):
    """Tests the complete system workflow"""
    
    def setUp(self):
        """Initialises fresh controller for each test"""
        self.controller = MainController()
        # Clear default resources for testing
        self.controller.dispatcher.resources = []
        
    def test_complete_incident_lifecycle(self):
        """Tests full incident lifecycle from creation to resolution"""
        print("\n=== Starting Test: Complete Incident Lifecycle ===")
        
        # 1. Add sufficient test resources (extra ambulance)
        resources = [
            Resource("ambulance", "Zone 1"),
            Resource("ambulance", "Zone 2"),  # Extra ambulance
            Resource("fire_engine", "Zone 2"),
            Resource("police_car", "Zone 3")
        ]
        for r in resources:
            self.controller.dispatcher.add_resource(r)
        
        # 2. Report first incident (high priority but limited resources)
        incident1 = Incident(
            incident_type="fire",
            location="Zone 2",
            priority="high",
            required_resources=["fire_engine"]  # Only needs fire engine
        )
        self.controller.dispatcher.add_incident(incident1)
        
        # 3. Verify first assignment
        self.assertEqual(incident1.status, "assigned")
        
        # 4. Report critical incident (needs ambulance + fire engine)
        critical_incident = Incident(
            incident_type="explosion",
            location="Zone 1",
            priority="high",
            required_resources=["ambulance", "fire_engine"]
        )
        self.controller.dispatcher.add_incident(critical_incident)
        
        # 5. Verify reallocation occurred
        self.assertEqual(critical_incident.status, "assigned",
                        "Critical incident should be assigned")
        self.assertEqual(incident1.status, "unassigned",
                        "Original incident should be unassigned after reallocation")
        
        # 6. Resolve critical incident
        self.controller.dispatcher.resolve_incident(critical_incident.id)
        
        # 7. Verify final state
        for resource in self.controller.dispatcher.resources:
            self.assertTrue(resource.is_available,
                        f"{resource.resource_type} should be available after resolution")
        
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