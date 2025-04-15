"""
Represents an emergency response resource (e.g., ambulance, fire engine) with its attributes and availability status.
"""

class Resource:
    """
    A deployable emergency resource with type, location, and availability status.

    Attributes:
        resource_type (str): The type of resource (e.g., "ambulance", "fire_engine").
        location (str): The zone where the resource is stationed (e.g., "Zone 1").
        is_available (bool): Whether the resource is free for assignment (default True).
        assigned_incident (str|None): ID of incident assigned to (None if unassigned).
    """
    
    def __init__(self, resource_type: str, location: str):
        self.resource_type = resource_type
        self.location = location
        self.is_available = True  # Default to available
        self.assigned_incident = None  # No assignment initially

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

    def __str__(self) -> str:
        """
        String representation for debugging/logging.

        Returns:
            str: Formatted resource details.
        """
        status = "Available" if self.is_available else f"Assigned to {self.assigned_incident}"
        return f"{self.resource_type:15} | {self.location:10} | {status}"