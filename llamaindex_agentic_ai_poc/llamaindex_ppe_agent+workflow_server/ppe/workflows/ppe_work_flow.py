import logging

import dotenv
import llama_index.core
import llama_index.core.agent
from llama_index.core.llms.llm import LLM
from llama_index.core.memory import Memory
from workflows import Workflow, Context, step
from workflows.events import StopEvent


import ppe.mcp_client.mcp_client
import ppe.workflows.agents.ppe_agents
import ppe.workflows.ppe_predictor.ppe_tools
from ppe.config.config import (ContextProvider)
from ppe.workflows.events.ppe_events import (
    ImageUploadedEvent,
    ViolationsFoundEvent,
    NoViolationsFoundEvent
)

dotenv.load_dotenv()




class PPEWorkFlow(Workflow):

    def __init__(self, context_provider: ContextProvider, **kwargs):
        super().__init__(**kwargs)
        self.name = "ppe_work_flow"
        self.llm = llama_index.core.Settings.llm
        self.context_provider=context_provider
        self.agent : llama_index.core.agent.FunctionAgent = None


    @step
    async def analyse_image(self, ctx: Context, ev: ImageUploadedEvent) -> NoViolationsFoundEvent | ViolationsFoundEvent:

        async with ctx.store.edit_state() as state:
            # initialise state
            ppe_request = {"user_id":ev.user_id,"site_id":ev.site_id,"image":ev.image}
            state['ppe_request'] = ppe_request
            state['session_key'] = self.get_session_key(ppe_request)
            await self.set_up(llm=llama_index.core.Settings.llm)

        memory: Memory = await self.context_provider.get_memory(key=state['session_key'])

        violations = await ppe.workflows.ppe_predictor.ppe_tools.ppe_risk_analyser(ev.user_id, ev.site_id, ev.image)

        if violations and violations == True:
            ctx.send_event(
                message=ViolationsFoundEvent(msg="Violations Found")
            )
        else:
            ctx.send_event(
                message=NoViolationsFoundEvent(msg="No Violations Found")
            )

    @step
    async def handle_ppe_violations(self, ctx: Context, ev:  NoViolationsFoundEvent | ViolationsFoundEvent) -> StopEvent:
        if isinstance(ev, NoViolationsFoundEvent):
            return StopEvent(result="No issues found")
        else:

            async with ctx.store.edit_state() as state:
                memory: Memory = await self.context_provider.get_memory(key=state['session_key'])
                ppe_request = state['ppe_request']
                response = await self.agent.run(
                    user_msg=f""" create incident  {{"kwargs": {{"user_id": {ppe_request['user_id']}, "site_id": "{ppe_request['site_id']}" }} and finally return incident_id as response""",
                    memory=memory
                )
                state['ppe_request']['incident'] = response.response.content
                logging.info(f"Incident Created {response}")
                return StopEvent(result=state['ppe_request'])

    def get_session_key(self, ev:ImageUploadedEvent) -> str:
        return "_".join([ev['user_id'],ev['site_id'],ev['image']])


    async def set_up(self, llm:LLM):
        if self.agent is None:
            tools = await ppe.mcp_client.mcp_client.get_tools_from_mcp_server()
            tools.append(llama_index.core.tools.FunctionTool.from_defaults(fn=ppe.workflows.ppe_predictor.ppe_tools.ppe_risk_analyser))
            self.agent = ppe.workflows.agents.ppe_agents.get_image_analyser_agent(llm=llm, tools=tools)







def get_work_flow():
    ppe_work_flow = PPEWorkFlow(ContextProvider())
    return ppe_work_flow
