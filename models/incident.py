import uuid # Adds automatic UUIDs generation for incidents

# models/incident.py
class Incident:
    """
    Represents an emergency incident with type, location, priority, and required resources.
    
    Attributes:
        id (str): Unique identifier for the incident
        type (str): The type of emergency (e.g., "fire", "accident").
        location (str): The zone where the incident occurred (e.g., "Zone 1").
        priority (str): Severity level ("high", "medium", "low").
        required_resources (list): Resources needed (e.g., ["ambulance", "police"]).
        status (str): Current assignment state (defaults to "unassigned").
    """
    _id_counter = 0  # Class variable for sequential IDs

    def __init__(self, incident_type: str, location: str, priority: str, required_resources: list):
        Incident._id_counter += 1
        self.id = f"INC-{Incident._id_counter:04d}"  # Format as INC-0001
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

    def get_assigned_resources(self, dispatcher) -> list:
        """
        Returns list of resources currently assigned to this incident.
        
        Args:
            dispatcher: The Dispatcher instance managing resources
            
        Returns:
            list: List of Resource objects assigned to this incident
        """
        return [r for r in dispatcher.resources 
                if r.assigned_incident == self.id]
    
    def update_status(self, dispatcher):
        """Dynamic status update based on actual resource assignments"""
        assigned_resources = [r for r in dispatcher.resources 
                            if r.assigned_incident == self.id]
        self.status = "assigned" if assigned_resources else "unassigned"