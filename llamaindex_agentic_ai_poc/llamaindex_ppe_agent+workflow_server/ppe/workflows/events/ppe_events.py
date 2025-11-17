"""PPE workflow event definitions.

This module defines all event types used in the PPE workflow system,
including start events, intermediate events, and stop events.
"""

import pydantic
from pydantic import Field
from workflows.events import StartEvent, Event, StopEvent


class PPERequest(pydantic.BaseModel):
    """Base model for PPE request data.

    This is a placeholder model that can be extended with specific
    PPE request fields as needed.
    """
    pass


class ImageUploadedEvent(StartEvent):
    """Event triggered when an image is uploaded for PPE analysis.

    Attributes:
        user_id: Identifier for the user who uploaded the image.
        site_id: Identifier for the site where the image was captured.
        image: Base64-encoded image data for analysis.
    """
    user_id: str = Field(alias='user_id')
    site_id: str = Field(alias='site_id')
    image: str = Field(alias='image')


class ViolationsFoundEvent(Event):
    """Event indicating that PPE violations were detected in an image.

    Attributes:
        msg: Message describing the violations found in the analyzed image.
    """
    msg: str = Field(..., description="Message describing an image analyzed")


class IncidentCreatedEvent(Event):
    """Event indicating that an incident was successfully created.

    Attributes:
        msg: Message confirming that an incident was created.
    """
    msg: str = Field(..., description="Incident was created.")


class NoViolationsFoundEvent(Event):
    """Event indicating that no PPE violations were found in an image.

    Attributes:
        msg: Message confirming that no violations were detected.
    """
    msg: str = Field(..., description="No Violations were found.")
