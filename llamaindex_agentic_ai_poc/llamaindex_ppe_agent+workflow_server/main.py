import asyncio
import logging
import os
import warnings

import dotenv
import workflows.server

import ppe.workflows.ppe_work_flow
import sys
warnings.filterwarnings("ignore")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

dotenv.load_dotenv()
server = workflows.server.WorkflowServer()
ppe_work_flow = ppe.workflows.ppe_work_flow.get_work_flow()
server.add_workflow(name=ppe_work_flow.name, workflow=ppe_work_flow)


async def main():
    host = os.environ.get("WORKFLOWS_PY_SERVER_HOST")
    port = int(os.environ.get("WORKFLOWS_PY_SERVER_PORT"))
    await server.serve(host = host, port = port)

if __name__ == "__main__":
     asyncio.run(main())