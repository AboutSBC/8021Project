from typing import Any, Dict, List, Optional, Tuple

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.prompt.context import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.mytool import sentiment_anlysis


class ContextAgent(ToolCallAgent):
    """A professional insurance needs analyst responsible for analyzing user input, identifying user needs and emotional states, and providing clear labels for potential customers.

    This agent focuses on understanding user needs, analyzing emotional states, and generating
    accurate labels to facilitate subsequent insurance product matching.
    """

    name: str = "context"
    description: str = (
        "A professional insurance needs analyst for identifying user needs and emotional states."
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 5

    # Add tools specific to context analysis
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            sentiment_anlysis(),
            Terminate(),
        )
    )

    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])
