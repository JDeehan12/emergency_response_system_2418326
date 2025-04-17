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
                    logging.info(f"Resources allocated to incident {incident.id}")
                elif incident.priority == 'high':
                    reallocated = self._reallocate_for_high_priority(incident)
                    if reallocated:
                        incident.status = 'assigned'
                        logging.info(f"Resources reallocated to high-priority incident {incident.id}")

    def _assign_resources_to_incident(self, incident: Incident) -> bool:
        """
        Assigns all required resources to an incident.
        Returns True if all resources were assigned, False otherwise.
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
        """
        Reallocates ALL required resources from lower priority incidents.
        Returns True if all resources were reallocated, False otherwise.
        """
        resources_needed = incident.required_resources.copy()
        reallocated_resources = []

        for resource_type in incident.required_resources:
            if resource_type in resources_needed:
                donor_resource = self._find_reallocatable_resource(resource_type)
                if donor_resource:
                    current_incident = self._get_incident_by_id(donor_resource.assigned_incident)
                    donor_resource.release()
                    current_incident.status = "unassigned"
                    donor_resource.assign_to_incident(incident.id)
                    reallocated_resources.append(donor_resource)
                    resources_needed.remove(resource_type)

        if not resources_needed:
            logging.info(f"Reallocated all resources for incident {incident.id}")
            return True
        else:
            logging.warning(f"Could not reallocate all resources for incident {incident.id}. Missing: {resources_needed}")

            # Rollback partial reallocation
            for resource in reallocated_resources:
                resource.release()
            return False

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
        """
        Calculates simple distance between two zones.
        Example: Zone 1 and Zone 3 -> distance 2
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
        Resolve the incident and release all assigned resources.

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
        """Release all resources of specific type"""
        for r in self.resources:
            if r.resource_type == resource_type and not r.is_available:
                r.release()

    def _assign_resources_to_incident(self, incident):
        # Clear existing assignments and log entries
        for key in [k for k in self.allocation_log if k.startswith(incident.id)]:
            del self.allocation_log[key]
        
        # Attempt new assignment
        success = True
        for res_type in incident.required_resources:
            resource = self._find_optimal_resource(res_type, incident.location, incident)
            if not resource:
                success = False
                break
            resource.assign_to_incident(incident.id)
            self.allocation_log[f"{incident.id}_{res_type}"] = resource.id  # Log the assignment
        
        incident.update_status(self)
        return success


