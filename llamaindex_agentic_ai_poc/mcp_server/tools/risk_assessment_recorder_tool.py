"""Risk assessment recorder tool for MCP server.

This module provides tools for recording PPE incidents and managing
risk assessment data through the Model Context Protocol server.
"""

import logging
import traceback
from typing import List
from uuid import uuid4

from llama_index.core.tools import ToolMetadata
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from pydantic import BaseModel, Field
from ultralytics import YOLO

logger = logging.getLogger("llama_index")

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")

# Global list to store incidents (in production, this should be a database)
incidents = list()


class PpeIncidents(BaseModel):
    """Model representing a PPE incident record.

    This Pydantic model defines the structure for PPE incident data,
    including user identification, site information, and incident status.

    Attributes:
        user_id: Identifier for the user associated with the incident.
        site_id: Identifier for the site where the incident occurred.
        incident_id: Unique identifier for the incident, or None if not yet created.
        state: Current state of the incident (e.g., "OPEN", "CLOSED").
    """
    user_id: str = Field(..., description="User ID")
    site_id: str = Field(..., description="Site ID")
    incident_id: str | None = Field(..., description="Incident ID")
    state: str = Field(..., description="Incident State")


class RiskAssesmentToolSpec(BaseToolSpec):
    """Tool specification for PPE risk assessment and incident recording.

    This class provides tools for creating and managing PPE incidents.
    For local testing, the YOLO model is placed inside the MCP server.
    In production, it should be deployed in the cloud with a URL provided
    via environment variable.

    Attributes:
        _yolo_model: YOLO model instance for object detection.
        spec_functions: List of function names exposed as tools.
        func_to_metadata_mapping: Mapping of function names to tool metadata.
    """

    # For local testing yolo model has been placed inside mcp server.
    # In prod it needs to be deployed in cloud and url should be given
    # using environment variable
    _yolo_model = YOLO('tools/predict/best.pt')

    spec_functions: List[str] = ['incident_recorder']

    func_to_metadata_mapping = {
        "incident_recorder": ToolMetadata(
            name="Incident Recorder",
            description=(
                "Create incident for user_id and site_id and return PpeIncidents"
            ),
            return_direct=True
        )
    }

    async def incident_recorder(*args, **kwargs) -> str:
        """Create an incident record for a user and site.

        Processes keyword arguments to extract user_id and site_id,
        creates a new incident with a unique UUID, and stores it in
        the incidents list. In production, this should interact with
        a proper database or API.

        Args:
            *args: Variable positional arguments (not used).
            **kwargs: Keyword arguments containing user_id and site_id.
                Expected format: {"kwargs": {"user_id": str, "site_id": str}}

        Returns:
            String representation of the generated incident UUID.

        Raises:
            Exception: If incident creation fails for any reason.
        """
        try:
            global user_id
            global site_id
            logger.info(f"{kwargs}")

            # Extract user_id and site_id from kwargs
            for key, value in kwargs.items():
                if key == "kwargs" and isinstance(value, dict):
                    logger.info(type(value))
                    site_id = str(value['site_id'])
                    user_id = str(value['user_id'])

            logger.info(
                f'incident_recorder being called with {user_id} {site_id}'
            )
            # Call an existing API to create an incident based on violations found
            incident_id = str(uuid4())
            incident = PpeIncidents(
                user_id=user_id,
                site_id=site_id,
                state="OPEN",
                incident_id=incident_id
            )
            incidents.append(incident)
            logger.info(f'incident_id = {incident_id}')
            return str(incident_id)

        except Exception as e:
            logger.error(f'incident_recorder failed  {e}')
            traceback.print_exc()
            raise e
