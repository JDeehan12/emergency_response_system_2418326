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
        """
        Core allocation logic with priority handling and reallocation.
        Processes incidents in priority order (high > medium > low).
        """
        # Process by priority
        for priority in ['high', 'medium', 'low']:
            unassigned = [i for i in self.incidents 
                         if i.priority == priority 
                         and i.status == 'unassigned']
            
            for incident in unassigned:
                if self._assign_resources_to_incident(incident):
                    incident.status = "assigned"
                elif priority == 'high':
                    self._reallocate_for_high_priority(incident)

    def _assign_resources_to_incident(self, incident: Incident) -> bool:
        """
        Attempts to assign all required resources to an incident.
        Returns True if all resources were assigned, False otherwise.
        """
        required = incident.required_resources.copy()
        
        for resource_type in required:
            resource = self._find_optimal_resource(resource_type, incident.location)
            if resource:
                resource.assign_to_incident(incident.id)
                self.allocation_log[incident.id] = resource.resource_type
                required.remove(resource_type)
        
        return len(required) == 0

    def _find_optimal_resource(self, resource_type: str, location: str) -> Optional[Resource]:
        """
        Finds the best available resource considering both type and proximity.
        Priority:
        1. Matching type at exact location
        2. Matching type at nearest location
        """
        # Get all available matching resources
        candidates = [r for r in self.resources 
                     if r.resource_type == resource_type 
                     and r.is_available]
        
        if not candidates:
            return None
            
        # Check for exact location match first
        for resource in candidates:
            if resource.location == location:
                return resource
                
        # Find nearest available resource
        return min(
            candidates,
            key=lambda x: self._location_distance(x.location, location)
        )

    def _reallocate_for_high_priority(self, incident: Incident) -> None:
        """
        Reallocates resources from lower priority incidents to a high priority incident.
        """
        for resource_type in incident.required_resources:
            # Find a reallocatable resource
            donor_resource = self._find_reallocatable_resource(resource_type)
            if donor_resource:
                # Get the incident currently using this resource
                current_incident = self._get_incident_by_id(donor_resource.assigned_incident)
                
                # Release the resource
                donor_resource.release()
                current_incident.status = "unassigned"
                
                # Reassign to high priority incident
                donor_resource.assign_to_incident(incident.id)
                self.allocation_log[incident.id] = donor_resource.resource_type
                
                # Re-process the unassigned incident
                self._allocate_resources()
                break  # Only reallocate one resource at a time

    def _find_reallocatable_resource(self, resource_type: str) -> Optional[Resource]:
        """
        Finds a resource that can be reallocated, prioritizing:
        1. Resources assigned to lowest priority incidents
        2. Resources at nearest locations
        """
        candidates = []
        for resource in self.resources:
            if (resource.resource_type == resource_type 
                and not resource.is_available
                and resource.assigned_incident):
                
                incident = self._get_incident_by_id(resource.assigned_incident)
                candidates.append((resource, incident))
        
        if not candidates:
            return None
            
        # Sort by priority (lowest first) then by distance
        candidates.sort(key=lambda x: (
            ['low', 'medium', 'high'].index(x[1].priority),
            self._location_distance(x[0].location, x[1].location)
        ))
        
        return candidates[0][0]

    def _get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        """Retrieves an incident by its ID."""
        for incident in self.incidents:
            if incident.id == incident_id:
                return incident
        return None

    def _location_distance(self, loc1: str, loc2: str) -> int:
        """
        Calculates simple distance between two zones.
        Example: Zone 1 and Zone 3 -> distance 2
        """
        zone1 = int(loc1.split()[1])
        zone2 = int(loc2.split()[1])
        return abs(zone1 - zone2)