# models/incident.py
class Incident:
    """
    Represents an emergency incident with type, location, priority, and required resources.
    
    Attributes:
        type (str): The type of emergency (e.g., "fire", "accident").
        location (str): The zone where the incident occurred (e.g., "Zone 1").
        priority (str): Severity level ("high", "medium", "low").
        required_resources (list): Resources needed (e.g., ["ambulance", "police"]).
        status (str): Current assignment state (defaults to "unassigned").
    """
    def __init__(self, incident_type: str, location: str, priority: str, required_resources: list):
        self.type = incident_type
        self.location = location
        self.priority = priority
        self.required_resources = required_resources
        self.status = "unassigned"  # Default status

    def update_priority(self, new_priority: str):
        """
        Updates the priority level of the incident.

        Args:
            new_priority (str): Must be "high", "medium", or "low".
        """
        self.priority = new_priority

    def set_status(self, new_status: str):
        """
        Modifies the assignment status of the incident.

        Args:
            new_status (str): E.g., "unassigned", "assigned", "resolved".
        """
        self.status = new_status