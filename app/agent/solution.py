from typing import List

from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.prompt.solution import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection

# from app.tool.chart_visualization.chart_prepare import VisualizationPrepare
# from app.tool.chart_visualization.data_visualization import DataVisualization
# from app.tool.chart_visualization.python_execute import NormalPythonExecute
from app.tool.mytool2 import rag


class SolutionAgent(ToolCallAgent):
    """
    A solution agent that finalizes the reply and ensures it meets standards.

    This agent is responsible for filtering prohibited language, privacy information,
    and ensuring the final response complies with insurance industry compliance requirements.
    """

    name: str = "solution"
    description: str = (
        "A solution agent that finalizes the reply and ensures it meets standards."
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 15000
    max_steps: int = 20

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            NormalPythonExecute(),
            VisualizationPrepare(),
            DataVisualization(),
            rag(),
            Terminate(),
        )
    )

    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])
