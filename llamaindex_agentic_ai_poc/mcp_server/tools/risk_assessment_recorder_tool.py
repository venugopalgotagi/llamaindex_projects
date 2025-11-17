import logging
from typing import List
from uuid import UUID
from uuid import uuid4
import traceback

from llama_index.core.tools import ToolMetadata
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from ultralytics import YOLO

logger = logging.getLogger("llama_index")

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")

from pydantic import BaseModel, Field
class PpeIncidents(BaseModel):
    user_id:str= Field(..., description="User ID")
    site_id:str= Field(..., description="Site ID")
    incident_id:str|None= Field(..., description="Incident ID")
    state:str= Field(..., description="Incident State")




incidents = list()

class RiskAssesmentToolSpec(BaseToolSpec):
    #For local testing yolo model has been placed inside mcp server.In prod it needs to be deployed in cloud and url should be given using environment variable
    _yolo_model = YOLO('tools/predict/best.pt')

    spec_functions: List[str] = [ 'incident_recorder']

    func_to_metadata_mapping = {
        "incident_recorder": ToolMetadata(
            name="Incident Recorder",
            description="Create incident for user_id and site_id and return PpeIncidents",
            return_direct=True
        )
    }

    async def incident_recorder(*args, **kwargs) -> str:
        """
        Create incident for user_id and site_id and return PpeIncidents
        :param site_id:
        :param site_id:
        :return: incident_id UUID
        """
        try:
            global user_id
            global site_id
            logger.info(f"{kwargs}")

            for key, value in kwargs.items():
                if key == "kwargs" and type(value) == dict:
                    logger.info(type(value))
                    site_id = str(value['site_id'])
                    user_id = str(value['user_id'])

            logger.info(f'incident_recorder being called with {user_id} {site_id}')
            # call an existing api to create an incident based on violations found
            incident_id = str(uuid4())
            incident = PpeIncidents(user_id=user_id, site_id=site_id, state="OPEN", incident_id=incident_id)
            incidents.append(incident)
            logger.info(f'incident_id = {incident_id}')
            return str(incident_id)

        except Exception as e:
            logger.error(f'incident_recorder failed  {e}')
            traceback.print_exc()
            raise e