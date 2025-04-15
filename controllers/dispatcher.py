"""
Handles the allocation and reallocation of emergency resources to incidents.
Manages priority-based distribution and proximity considerations.
"""

from typing import List, Dict, Optional
from models.incident import Incident
from models.resource import Resource

class Dispatcher:
    """
    Coordinates resource allocation based on incident priority and resource availability.
    """

    def __init__(self):
        """Initialises a new Dispatcher with empty tracking lists."""
        self.incidents: List[Incident] = []
        self.resources: List[Resource] = []
        self.allocation_log: Dict[str, str] = {}

    def add_incident(self, incident: Incident) -> None:
        """Registers a new incident and triggers automatic allocation."""
        self.incidents.append(incident)
        self._allocate_resources()

    def add_resource(self, resource: Resource) -> None:
        """Adds a new resource to the available pool."""
        self.resources.append(resource)

    def _allocate_resources(self) -> None:
        """Core allocation logic with guaranteed priority handling."""
        # Process incidents in strict priority order
        for priority in ['high', 'medium', 'low']:
            # Get unassigned incidents of current priority
            incidents = [i for i in self.incidents 
                        if i.priority == priority 
                        and i.status == 'unassigned']
            
            for incident in incidents:
                # Try to allocate all required resources
                success = True
                for resource_type in incident.required_resources:
                    resource = self._find_available_resource(resource_type, incident.location)
                    if not resource:
                        success = False
                        break
                    resource.assign_to_incident(incident.id)
                    self.allocation_log[incident.id] = resource.resource_type
                
                if success:
                    incident.status = "assigned"
                elif priority == 'high':
                    # For high-priority incidents, try to reallocate
                    self._reallocate_for_incident(incident)

    def _find_available_resource(self, 
                               resource_type: str, 
                               location: str) -> Optional[Resource]:
        """Finds the best available resource matching type and location."""
        # First try for exact location match
        for resource in self.resources:
            if (resource.resource_type == resource_type 
                and resource.is_available 
                and resource.location == location):
                return resource
        
        # Fallback to type match only
        for resource in self.resources:
            if (resource.resource_type == resource_type 
                and resource.is_available):
                return resource
        return None

    def _reallocate_for_incident(self, incident: Incident) -> None:
        """Reallocates resources from lower-priority incidents."""
        # Find lower priority incidents that have needed resources
        for existing_incident in sorted(
            [i for i in self.incidents 
             if i.priority in ['medium', 'low'] 
             and i.status == "assigned"],
            key=lambda x: ['medium', 'low'].index(x.priority)
        ):
            # Check each resource assigned to this incident
            for resource in [r for r in self.resources 
                           if r.assigned_incident == existing_incident.id
                           and r.resource_type in incident.required_resources]:
                # Release the resource first
                resource.is_available = True
                resource.assigned_incident = None
                existing_incident.status = "unassigned"
                
                # Then assign it to the high-priority incident
                resource.assign_to_incident(incident.id)
                incident.status = "assigned"
                self.allocation_log[incident.id] = resource.resource_type
                return  # Stop after first successful reallocation