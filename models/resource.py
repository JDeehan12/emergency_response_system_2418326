"""
Represents an emergency response resource (e.g., ambulance, fire engine) with its attributes and availability status.
"""
import uuid # Adds automatic UUIDs generation for resources

RESOURCE_TYPES = {
    1: {"id": "ambulance", "name": "Ambulance", "aliases": ["medic", "paramedic"]},
    2: {"id": "fire_engine", "name": "Fire Engine", "aliases": ["firetruck", "fire"]},
    3: {"id": "police_car", "name": "Police Car", "aliases": ["police", "patrol"]}
}

class Resource:
    """
    A deployable emergency resource with type, location, and availability status.
    """
    
    def __init__(self, resource_type: str, location: str):
        """
        Initialise a new resource.
        
        Args:
            resource_type: Must match an id from RESOURCE_TYPES
            location: Zone identifier (e.g. "Zone 1")
        """
        if not any(r["id"] == resource_type for r in RESOURCE_TYPES.values()):
            raise ValueError(f"Invalid resource type. Must be one of: {[r['id'] for r in RESOURCE_TYPES.values()]}")
        
        self.id = f"RES-{uuid.uuid4().hex[:6]}"  # 6-char unique ID
        self.resource_type = resource_type
        self.location = location
        self.is_available = True
        self.assigned_incident = None

    def toggle_availability(self, new_status: bool) -> None:
        """
        Updates the availability status of the resource.

        Args:
            new_status (bool): True if available, False if allocated.
        """
        self.is_available = new_status
        if not new_status:
            self.assigned_incident = None  # Clear assignment when made available

    def assign_to_incident(self, incident_id: str) -> None:
        """
        Marks the resource as allocated to a specific incident.

        Args:
            incident_id (str): Unique identifier of the incident.
        """
        if self.is_available:
            self.assigned_incident = incident_id
            self.is_available = False
        else:
            raise ValueError("Resource already allocated to another incident")

    def release(self) -> None:
        """
        Releases the resource from its current assignment and marks it as available.
        """
        self.assigned_incident = None
        self.is_available = True

    def __str__(self) -> str:
        """
        String representation for debugging/logging.

        Returns:
            str: Formatted resource details.
        """
        status = "Available" if self.is_available else f"Assigned to {self.assigned_incident}"
        return f"{self.resource_type:15} | {self.location:10} | {status}"
