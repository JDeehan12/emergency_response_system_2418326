"""
Handles the allocation and reallocation of emergency resources to incidents.
Manages priority-based distribution and proximity considerations.
"""

import logging
from typing import List, Dict, Optional
from models.incident import Incident
from models.resource import Resource

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class IncidentNotFoundError(Exception):
    """Custom exception for when an incident cannot be found by ID."""
    pass

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
        Manages complete resource allocation process.
        """
        return self._allocate_resources()

    def _allocate_resources(self) -> dict:
        """
        Revised allocation logic that properly handles:
        - Multiple high-priority incidents
        - Resource constraints
        - New resource additions
        - Newer high-priority incidents taking precedence over older ones
        """
        # Release all resources to start with clean state
        for incident in self.incidents:
            incident.status = 'unassigned'
        for resource in self.resources:
            resource.release()
        
        # Sort incidents by priority (high first) and then by timestamp (newest first)
        sorted_incidents = sorted(
            self.incidents,
            key=lambda x: (
                ['high', 'medium', 'low'].index(x.priority),
                -x.timestamp  # Newer incidents come first
            )
        )

        # Phase 1: Assign all high-priority incidents with available resources
        high_priority_incidents = [i for i in sorted_incidents if i.priority == 'high']
        for incident in high_priority_incidents:
            if not self._assign_resources_to_incident(incident):
                # If normal assignment fails, try force assignment
                self._force_assign_high_priority(incident)

        # Phase 2: Assign remaining incidents
        for incident in sorted_incidents:
            if incident.status != 'assigned':
                self._assign_resources_to_incident(incident)

        # Prepare results
        assigned = [i.id for i in self.incidents if i.status == 'assigned']
        unassigned = [i.id for i in self.incidents if i.status == 'unassigned']
        
        logging.info(f"Allocation completed - Assigned: {len(assigned)}, Unassigned: {len(unassigned)}")
        return {
            'assigned': assigned,
            'unassigned': unassigned
        }

    def _force_assign_high_priority(self, incident: Incident) -> bool:
        """
        Final version with timestamp-based reallocation.
        Only reallocates from older incidents of same priority or lower priorities.
        """
        if incident.priority != 'high':
            return False

        required_resources = set(incident.required_resources)
        assigned_resources = []

        for resource_type in required_resources:
            # First try available resources
            resource = self._find_optimal_resource(resource_type, None, incident)
            if resource and resource.is_available:
                resource.assign_to_incident(incident.id)
                assigned_resources.append(resource)
                continue

            # If none available, find reallocatable resource
            resource = self._find_reallocatable_resource(resource_type)
            if resource:
                current_incident = self._get_incident_by_id(resource.assigned_incident)
                # Only reallocate from lower priority or older same-priority incidents
                if (current_incident.priority != 'high' or 
                    (current_incident.priority == 'high' and current_incident.timestamp < incident.timestamp)):
                    resource.release()
                    current_incident.status = 'unassigned'
                    resource.assign_to_incident(incident.id)
                    assigned_resources.append(resource)
                    continue

        # Verify all resources were assigned
        if all(r in [res.resource_type for res in assigned_resources] 
            for r in incident.required_resources):
            incident.status = 'assigned'
            logging.info(f"FORCE ASSIGNED: Resources allocated to high-priority incident {incident.id}")
            return True

        # If failed, rollback any partial assignments
        for resource in assigned_resources:
            resource.release()
        incident.status = 'unassigned'
        return False

    def _assign_resources_to_incident(self, incident: Incident) -> bool:
        """
        Assigns required resources to an incident using optimal available resources.
        
        Args:
            incident: The incident requiring resources
            
        Returns:
            bool: True if all resources were assigned, False otherwise
        """
        required_resources = set(incident.required_resources)
        assigned_resources = []
        
        try:
            # Attempt to assign resources in the same zone
            for resource_type in list(required_resources):
                resource = self._find_optimal_resource(resource_type, incident.location, incident)
                if resource:
                    resource.assign_to_incident(incident.id)
                    assigned_resources.append(resource)
                    required_resources.remove(resource_type)
                    self.allocation_log[f"{incident.id}_{resource.id}"] = resource.resource_type
            
            # Attempt to assign any available resources for unmet needs
            for resource_type in list(required_resources):
                resource = self._find_optimal_resource(resource_type, None, incident)
                if resource:
                    resource.assign_to_incident(incident.id)
                    assigned_resources.append(resource)
                    required_resources.remove(resource_type)
                    self.allocation_log[f"{incident.id}_{resource.id}"] = resource.resource_type
            
            if required_resources:
                raise ValueError("Could not assign all required resources")
                
            incident.status = "assigned"
            logging.info(f"ASSIGNED: Resources successfully allocated to incident {incident.id}")
            return True
            
        except ValueError:
            # Roll back any partial assignments on failure
            for resource in assigned_resources:
                resource.release()
                if f"{incident.id}_{resource.id}" in self.allocation_log:
                    del self.allocation_log[f"{incident.id}_{resource.id}"]
            return False

    def _find_optimal_resource(self, resource_type: str, location: str, incident: Incident) -> Optional[Resource]:
        """
        Finds the best available resource matching the criteria.
        
        Args:
            resource_type: Type of resource needed
            location: Preferred location (None for any location)
            incident: The incident needing the resource
            
        Returns:
            Resource: The optimal resource if found, None otherwise
        """
        candidates = [r for r in self.resources
                      if r.resource_type == resource_type 
                      and r.is_available]
        
        if not candidates:
            return None
            
        # Prioritise same-zone resources if location specified
        if location:
            same_zone = [r for r in candidates if r.location == location]
            if same_zone:
                return same_zone[0]
        
        # Otherwise return closest available
        return min(
            candidates,
            key=lambda x: self._location_distance(x.location, incident.location)
        )

    def _reallocate_for_high_priority(self, incident: Incident) -> bool:
        """Uses force assignment for high-priority incidents."""
        return self._force_assign_high_priority(incident)

    def _find_reallocatable_resource(self, resource_type: str) -> Optional[Resource]:
        """
        Finds a resource that can be reallocated, prioritizing:
        1. Lowest priority incidents
        2. Older incidents of same priority
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

        # Sort by priority (lowest first) then by timestamp (oldest first)
        candidates.sort(key=lambda x: (
            ['low', 'medium', 'high'].index(x[1].priority),
            x[1].timestamp
        ))

        return candidates[0][0]

    def _get_incident_by_id(self, incident_id: str) -> Incident:
        """Retrieves an incident by its ID. Raises error if not found."""
        for incident in self.incidents:
            if incident.id == incident_id:
                return incident
        raise IncidentNotFoundError(f"No incident found with ID: {incident_id}")

    def _location_distance(self, loc1: str, loc2: str) -> int:
        """
        Calculates the distance between two zones by numeric difference.
        
        Note:
            Assumes zones are numbered linearly (e.g., 'Zone 1' → 'Zone 3' = distance 2).
            
        Returns:
            int: Absolute difference between zone numbers, or 100 if invalid format.
        """
        try:
            zone1 = int(loc1.split()[1])
            zone2 = int(loc2.split()[1])
            return abs(zone1 - zone2)
        except (IndexError, ValueError):
            logging.warning(f"Invalid location format: '{loc1}' or '{loc2}'")
            return 100  # Return high distance for invalid format

    def resolve_incident(self, incident_id):
        """
        Resolves the incident and releases all assigned resources.
        
        Args:
            incident_id: The ID of the incident being resolved
        """
        incident = next((i for i in self.incidents if i.id == incident_id), None)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found.")

        assigned_resources = incident.get_assigned_resources(self)
        for resource in assigned_resources:
            resource.release()
            if f"{incident.id}_{resource.id}" in self.allocation_log:
                del self.allocation_log[f"{incident.id}_{resource.id}"]

        incident.status = "resolved"
        logging.info(f"Resolved incident {incident_id}. Released resources: {[r.id for r in assigned_resources]}")

    def _release_resources_of_type(self, resource_type):
        """Releases all resources of specific type"""
        for r in self.resources:
            if r.resource_type == resource_type and not r.is_available:
                r.release()