from typing import Any, Dict, List, Optional, Tuple

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.prompt.objection import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.mytool import sentiment_anlysis
from app.tool.mytool3 import fin_sentiment_anlysis


class ObjectionAgent(ToolCallAgent):
    """An expert Objection-Handling Agent for insurance sales.

    This agent is designed to handle customer objections in insurance sales scenarios,
    providing persuasive and empathetic responses to address customer concerns.
    """

    name: str = "objection"
    description: str = "An expert Objection-Handling Agent for insurance sales."

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 10

    # Add tools specific to objection handling
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            sentiment_anlysis(),
            fin_sentiment_anlysis(),
            Terminate(),
        )
    )

    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])
