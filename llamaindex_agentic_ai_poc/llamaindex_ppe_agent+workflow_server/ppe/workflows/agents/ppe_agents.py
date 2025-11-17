from typing import List

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms.llm import LLM
from llama_index.core.tools.types import BaseTool


def get_image_analyser_agent(llm:LLM, tools:List[BaseTool]) -> FunctionAgent:
    return FunctionAgent(
        name='image_analyser',
        llm=llm,
        tools=tools,
        system_prompt="You are a Senior Manager who can analyse image for PPE violations and can create incident if any violations found. You should use the given ppe_predictor to achieve the goal.",
    )