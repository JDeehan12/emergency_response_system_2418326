"""
Handles the allocation and reallocation of emergency resources to incidents.
Manages priority-based distribution and proximity considerations.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from models.incident import Incident
from models.resource import Resource

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Remove the root: prefix
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
        """Manual allocation with clean state reset"""
        # Clear temporary assignments
        for incident in self.incidents:
            if incident.status == 'assigned':
                incident.status = 'unassigned'
                for r in self.resources:
                    if r.assigned_incident == incident.id:
                        r.release()
        
        # Perform fresh allocation
        self._allocate_resources()
        
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
                    logging.info(f"ASSIGNED: Resources successfully allocated to incident {incident.id}")
                elif incident.priority == 'high':
                    reallocated = self._reallocate_for_high_priority(incident)
                    if reallocated:
                        incident.status = 'assigned'
                        logging.info(f"REALLOCATED: Resources reallocated to high-priority incident {incident.id}")

    def _assign_resources_to_incident(self, incident: Incident) -> bool:
        """
        Assigns all required resources to an incident.

        Returns: 
            True if all resources were assigned, False otherwise.
            If assignment fails, releases any partially assigned resources.
        """
        assigned_resources = []
        all_assigned = True

        for resource_type in incident.required_resources:
            resource = self._find_optimal_resource(resource_type, incident.location, incident)
            if resource:
                resource.assign_to_incident(incident.id)
                assigned_resources.append(resource)
                self.allocation_log[f"{incident.id}_{resource_type}"] = resource.resource_type
            else:
                all_assigned = False
                break  # Stop if we can't assign one of the required resources

        if not all_assigned:
            # Rollback any partial assignments
            for resource in assigned_resources:
                resource.release()
            for key in [k for k in self.allocation_log if k.startswith(incident.id)]:
                del self.allocation_log[key]
            return False

        return True

    def _find_optimal_resource(self, resource_type: str, location: str, incident: Incident) -> Optional[Resource]:
        """
        Finds the best available resource considering both type and proximity.
        Includes incident parameter for future priority consideration.
        """
        candidates = [r for r in self.resources
                      if r.resource_type == resource_type and r.is_available]

        if not candidates:
            return None

        # Check for exact location match first
        for resource in candidates:
            if resource.location == location:
                return resource

        # Otherwise return the closest one
        return min(
            candidates,
            key=lambda x: self._location_distance(x.location, location)
        )

    def _reallocate_for_high_priority(self, incident: Incident) -> bool:
        """Attempts to reallocate resources from lower-priority incidents if needed.
        Args:
            incident: High-priority incident needing resources.

        Returns:
            bool: True if reallocation succeeded, False otherwise.
        """
        if incident.priority != "high":
            return False

        # First try normal assignment with any available resources
        if self._assign_resources_to_incident(incident):
            return True

        # Get currently assigned resources to this incident
        assigned_to_incident = [r for r in self.resources 
                            if r.assigned_incident == incident.id]
        
        # Calculate remaining needs
        remaining_needs = set(incident.required_resources) - {r.resource_type for r in assigned_to_incident}
        
        if not remaining_needs:
            return True

        # Try to satisfy each remaining need
        for resource_type in remaining_needs.copy():  # Create a copy for safe iteration
            # First try to find available resources of this type
            available = [r for r in self.resources 
                        if r.resource_type == resource_type and r.is_available]
            
            if available:
                available[0].assign_to_incident(incident.id)
                remaining_needs.remove(resource_type)
                continue
                
            # If no available, find reallocatable resource from lowest priority
            resource = self._find_reallocatable_resource(resource_type)
            if not resource:
                return False
                
            # Release from current assignment
            current_incident = self._get_incident_by_id(resource.assigned_incident)
            resource.release()
            current_incident.status = "unassigned"
            
            # Assign to new incident
            resource.assign_to_incident(incident.id)
            remaining_needs.remove(resource_type)

        return True

    def _find_reallocatable_resource(self, resource_type: str) -> Optional[Resource]:
        """
        Finds a resource that can be reallocated, prioritising:
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

    def _get_incident_by_id(self, incident_id: str) -> Incident:
        """Retrieves an incident by its ID. Raises error if not found."""
        for incident in self.incidents:
            if incident.id == incident_id:
                return incident
        raise IncidentNotFoundError(f"No incident found with ID: {incident_id}")

    def _location_distance(self, loc1: str, loc2: str) -> int:
        """Calculates the distance between two zones by numeric difference.
            Note:
                Assumes zones are numbered linearly (e.g., 'Zone 1' → 'Zone 3' = distance 2).

            Args:
                loc1: First zone (e.g., 'Zone 1').
                loc2: Second zone.
                
            Returns:
                int: Absolute difference between zone numbers, or 100 if invalid format.
            """
        try:
            zone1 = int(loc1.split()[1])
            zone2 = int(loc2.split()[1])
            return abs(zone1 - zone2)
        except (IndexError, ValueError):
            logging.warning(f"Invalid location format: '{loc1}' or '{loc2}'")
            return 100  # Return a high distance if format is wrong

    def resolve_incident(self, incident_id):
        """
        Resolves the incident and releases all assigned resources.

        Args:
            incident_id: The ID of the incident being resolved.
        """
        # Search for the incident in the list
        incident = next((i for i in self.incidents if i.id == incident_id), None)

        if not incident:
            raise ValueError(f"Incident {incident_id} not found.")

        # Get all resources assigned to this incident
        assigned_resources = incident.get_assigned_resources(self)
        
        # Release all assigned resources
        for resource in assigned_resources:
            resource.release()

        # Mark the incident as resolved
        incident.status = "resolved"

        # Log the released resources
        logging.info(f"Resolved incident {incident_id}. Released resources: {[r.id for r in assigned_resources]}")

    def _release_resources_of_type(self, resource_type):
        """Releases all resources of specific type"""
        for r in self.resources:
            if r.resource_type == resource_type and not r.is_available:
                r.release()

    def _assign_resources_to_incident(self, incident: Incident) -> bool:
        """
        Assigns all required resources to an incident.

        Returns: 
            True if all resources were assigned, False otherwise.
            If assignment fails, releases any partially assigned resources.
        """
        assigned_resources = []
        
        try:
            for resource_type in incident.required_resources:
                resource = self._find_optimal_resource(resource_type, incident.location, incident)
                if not resource:
                    raise ValueError(f"No available {resource_type}")
                    
                resource.assign_to_incident(incident.id)
                assigned_resources.append(resource)
                # Update allocation log with resource ID instead of type
                self.allocation_log[f"{incident.id}_{resource.id}"] = resource.resource_type
                
            incident.status = "assigned"
            return True
            
        except ValueError:
            # Rollback any partial assignments
            for resource in assigned_resources:
                resource.release()
            return False