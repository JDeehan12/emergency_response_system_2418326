"""
Handles the allocation and reallocation of emergency resources to incidents.
Manages priority-based distribution and proximity considerations.
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from models.incident import Incident
from models.resource import Resource
logging.basicConfig(level=logging.INFO)

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
        if not isinstance(incident, Incident):
            raise TypeError("Must provide Incident object")
        self.incidents.append(incident)
        self._allocate_resources()

    def add_resource(self, resource: Resource) -> None:
        """Adds a new resource to the available pool."""
        self.resources.append(resource)

    def allocate_resources(self) -> dict:
        """
        Manually triggers resource allocation and returns allocation report.
        
        Returns:
            dict: Allocation results with keys:
                - assigned: List of assigned incident IDs
                - unassigned: List of unassigned incident IDs
        """
        self._allocate_resources()  # This calls the existing allocation logic
        
        return {
            'assigned': [i.id for i in self.incidents if i.status == 'assigned'],
            'unassigned': [i.id for i in self.incidents if i.status == 'unassigned']
        }
    
    def _allocate_resources(self) -> None:
        """
        Iterates over unassigned incidents and tries to assign required resources.
        """
        for incident in self.incidents:
            if incident.status != 'assigned':
                success = self._assign_resources_to_incident(incident)
                if success:
                    incident.status = 'assigned'
                else:
                    # Try reallocation if incident has high priority
                    if incident.priority == 'high':
                        reallocated = self._reallocate_for_high_priority(incident)
                        if reallocated:
                            incident.status = 'assigned'
        
    def _assign_resources_to_incident(self, incident: Incident) -> bool:
        """
        Attempts to assign all required resources to an incident.
        Returns True if all resources were assigned, False otherwise.
        """
        required = set(incident.required_resources)  # Use set to avoid duplicates
        assigned_resources = []
        
        try:
            for resource_type in required:
                resource = self._find_optimal_resource(resource_type, incident.location, incident)
                if not resource:
                    raise ValueError(f"No available {resource_type} found")
                
                resource.assign_to_incident(incident.id)
                assigned_resources.append(resource)
                self.allocation_log[f"{incident.id}-{resource.id}"] = {
                    'resource_type': resource_type,
                    'time': datetime.now().isoformat(),
                    'location': resource.location
                }  

            incident.status = "assigned"
            return True
            
        except Exception as e:
            for resource in assigned_resources:
                resource.release()
            logging.warning(f"Assignment failed for {incident.id}: {str(e)}")
            return False

    def _find_optimal_resource(self, resource_type: str, location: str, incident: Incident) -> Optional[Resource]:
        """
        Finds the best available resource considering both type and proximity.
        Now excludes resources already assigned to other incidents.
        
        Args:
            resource_type: Type of resource needed
            location: Incident location (e.g., "Zone 1")
            incident: The incident we're assigning to
            
        Returns:
            The optimal available Resource or None
        """
        # Get available resources or resources already assigned to THIS incident
        candidates = [
            r for r in self.resources 
            if (r.resource_type == resource_type and 
                (r.is_available or r.assigned_incident == incident.id))
        ]
        
        if not candidates:
            return None
            
        # Prioritize exact location matches first
        exact_matches = [r for r in candidates if r.location == location]
        if exact_matches:
            return exact_matches[0]
            
        # Then find nearest available
        return min(
            candidates,
            key=lambda x: self._location_distance(x.location, location)
        )

    def _reallocate_for_high_priority(self, incident: Incident) -> bool:
        """
        Reallocates resources from lower priority incidents.
        Returns True if reallocation was successful, False otherwise.
        """
        for resource_type in incident.required_resources:
            donor_resource = self._find_reallocatable_resource(resource_type)
            if donor_resource:
                # Release from current incident
                current_incident = self._get_incident_by_id(donor_resource.assigned_incident)
                donor_resource.release()
                current_incident.status = "unassigned"
                
                # Assign to high priority incident
                donor_resource.assign_to_incident(incident.id)
                self.allocation_log[incident.id] = donor_resource.resource_type
                return True
        return False

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
