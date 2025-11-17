import pydantic
from pydantic import Field
from workflows.events import StartEvent, Event, StopEvent

class PPERequest(pydantic.BaseModel):
    ...


class ImageUploadedEvent(StartEvent):
    user_id: str = Field(alias='user_id')
    site_id: str = Field(alias='site_id')
    image: str = Field(alias='image')


class ViolationsFoundEvent(Event):
    msg: str= Field(...,description="Message describing an image analyzed")

class IncidentCreatedEvent(Event):
    msg:str = Field(...,description="Incident was created.")

class NoViolationsFoundEvent(Event):
    msg:str = Field(...,description="No Violations were found.")

