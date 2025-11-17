"""PPE agent definitions for workflow processing.

This module defines specialized agents used in PPE workflows for image
analysis and incident creation.
"""

from typing import List

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms.llm import LLM
from llama_index.core.tools.types import BaseTool


def get_image_analyser_agent(llm: LLM, tools: List[BaseTool]) -> FunctionAgent:
    """Create an image analyzer agent for PPE violation detection.

    This agent is configured as a Senior Manager capable of analyzing images
    for PPE violations and creating incidents when violations are found.

    Args:
        llm: Language model instance to use for the agent.
        tools: List of tools available to the agent, including PPE predictor.

    Returns:
        FunctionAgent configured for image analysis and incident creation.
    """
    return FunctionAgent(
        name='image_analyser',
        llm=llm,
        tools=tools,
        system_prompt=(
            "You are a Senior Manager who can analyse image for PPE violations "
            "and can create incident if any violations found. You should use "
            "the given ppe_predictor to achieve the goal."
        ),
    )
