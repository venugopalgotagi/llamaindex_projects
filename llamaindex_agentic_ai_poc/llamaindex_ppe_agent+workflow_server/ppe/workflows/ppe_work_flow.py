"""PPE workflow implementation.

This module defines the main workflow for processing PPE compliance
analysis, including image analysis, violation detection, and incident
creation.
"""

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
from ppe.config.config import ContextProvider
from ppe.workflows.events.ppe_events import (
    ImageUploadedEvent,
    ViolationsFoundEvent,
    NoViolationsFoundEvent
)

dotenv.load_dotenv()


class PPEWorkFlow(Workflow):
    """Workflow for processing PPE compliance analysis.

    This workflow handles the complete lifecycle of PPE compliance checking:
    1. Receives image upload events
    2. Analyzes images for PPE violations
    3. Creates incidents when violations are detected
    4. Manages memory and context throughout the process

    Attributes:
        name: Workflow identifier name.
        llm: Language model instance for agent operations.
        context_provider: Provider for memory and context management.
        agent: Function agent for image analysis and incident creation.
    """

    def __init__(self, context_provider: ContextProvider, **kwargs) -> None:
        """Initialize the PPE workflow.

        Args:
            context_provider: Provider for memory and context management.
            **kwargs: Additional arguments passed to parent Workflow class.
        """
        super().__init__(**kwargs)
        self.name = "ppe_work_flow"
        self.llm = llama_index.core.Settings.llm
        self.context_provider = context_provider
        self.agent: llama_index.core.agent.FunctionAgent = None

    @step
    async def analyse_image(
        self,
        ctx: Context,
        ev: ImageUploadedEvent
    ) -> NoViolationsFoundEvent | ViolationsFoundEvent:
        """Analyze uploaded image for PPE violations.

        This step processes an uploaded image, stores the request in state,
        loads memory for the session, and checks for PPE violations.

        Args:
            ctx: Workflow context for state management and event sending.
            ev: Image upload event containing user_id, site_id, and image data.

        Returns:
            ViolationsFoundEvent if violations are detected,
            NoViolationsFoundEvent if no violations are found.
        """
        async with ctx.store.edit_state() as state:
            # Initialize state
            ppe_request = {
                "user_id": ev.user_id,
                "site_id": ev.site_id,
                "image": ev.image
            }
            state['ppe_request'] = ppe_request
            state['session_key'] = self.get_session_key(ppe_request)
            await self.set_up(llm=llama_index.core.Settings.llm)

        memory: Memory = await self.context_provider.get_memory(
            key=state['session_key']
        )

        violations = await ppe.workflows.ppe_predictor.ppe_tools.ppe_risk_analyser(
            ev.user_id,
            ev.site_id,
            ev.image
        )

        if violations is True:
            ctx.send_event(
                message=ViolationsFoundEvent(msg="Violations Found")
            )
        else:
            ctx.send_event(
                message=NoViolationsFoundEvent(msg="No Violations Found")
            )

    @step
    async def handle_ppe_violations(
        self,
        ctx: Context,
        ev: NoViolationsFoundEvent | ViolationsFoundEvent
    ) -> StopEvent:
        """Handle PPE violation events.

        If no violations are found, stops the workflow. If violations are
        found, creates an incident using the agent and returns the result.

        Args:
            ctx: Workflow context for state management.
            ev: Event indicating whether violations were found or not.

        Returns:
            StopEvent with the workflow result, including incident details
            if violations were found.
        """
        if isinstance(ev, NoViolationsFoundEvent):
            return StopEvent(result="No issues found")
        else:
            async with ctx.store.edit_state() as state:
                memory: Memory = await self.context_provider.get_memory(
                    key=state['session_key']
                )
                ppe_request = state['ppe_request']
                response = await self.agent.run(
                    user_msg=(
                        f"""create incident {{"kwargs": {{"user_id": """
                        f"""{ppe_request['user_id']}, "site_id": """
                        f""""{ppe_request['site_id']}" }} and finally """
                        f"""return incident_id as response"""
                    ),
                    memory=memory
                )
                state['ppe_request']['incident'] = response.response.content
                logging.info(f"Incident Created {response}")
                return StopEvent(result=state['ppe_request'])

    def get_session_key(self, ev: dict) -> str:
        """Generate a unique session key from PPE request data.

        Args:
            ev: Dictionary containing user_id, site_id, and image data.

        Returns:
            Session key string formed by joining user_id, site_id, and image.
        """
        return "_".join([ev['user_id'], ev['site_id'], ev['image']])

    async def set_up(self, llm: LLM) -> None:
        """Set up the workflow agent with required tools.

        Initializes the image analyzer agent if not already created,
        loading tools from the MCP server and adding the PPE risk analyzer.

        Args:
            llm: Language model instance for the agent.
        """
        if self.agent is None:
            tools = await ppe.mcp_client.mcp_client.get_tools_from_mcp_server()
            tools.append(
                llama_index.core.tools.FunctionTool.from_defaults(
                    fn=ppe.workflows.ppe_predictor.ppe_tools.ppe_risk_analyser
                )
            )
            self.agent = ppe.workflows.agents.ppe_agents.get_image_analyser_agent(
                llm=llm,
                tools=tools
            )


def get_work_flow() -> PPEWorkFlow:
    """Create and return a configured PPE workflow instance.

    Returns:
        PPEWorkFlow instance initialized with a ContextProvider.
    """
    ppe_work_flow = PPEWorkFlow(ContextProvider())
    return ppe_work_flow
