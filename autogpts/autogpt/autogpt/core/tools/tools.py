from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional

if TYPE_CHECKING:
    from autogpt.agents.base import BaseAgent
    from autogpt.config import Any
    from .tool_parameters import ToolParameter
from autogpt.core.agents.simple.lib.models.context_items import ContextItem

ToolReturnValue = Any
ToolOutput = ToolReturnValue | tuple[ToolReturnValue, ContextItem]


class Tool:
    """A class representing a command.

    Attributes:
        name (str): The name of the command.
        description (str): A brief description of what the command does.
        parameters (list): The parameters of the function that the command executes.
    """

    def __init__(
        self,
        name: str,
        description: str,
        method: Callable[..., ToolOutput],
        parameters: list[ToolParameter],
        enabled: Literal[True] | Callable[[Any], bool] = True,
        disabled_reason: Optional[str] = None,
        aliases: list[str] = [],
        available: Literal[True] | Callable[[BaseAgent], bool] = True,
    ):
        self.name = name
        self.description = description
        self.method = method
        self.parameters = parameters
        self.enabled = enabled
        self.disabled_reason = disabled_reason
        self.aliases = aliases
        self.available = available

    @property
    def is_async(self) -> bool:
        return inspect.iscoroutinefunction(self.method)

    def __call__(self, *args, agent: BaseAgent, **kwargs) -> Any:
        # if callable(self.enabled) and not self.enabled(agent.legacy_config):
        #     if self.disabled_reason:
        #         raise RuntimeError(
        #             f"Tool '{self.name}' is disabled: {self.disabled_reason}"
        #         )
        #     raise RuntimeError(f"Tool '{self.name}' is disabled")

        # if callable(self.available) and not self.available(agent):
        #     raise RuntimeError(f"Tool '{self.name}' is not available")

        return self.method(*args, **kwargs, agent=agent)

    def __str__(self) -> str:
        params = [
            f"{param.name}: {param.spec.type.value if param.spec.required else f'Optional[{param.spec.type.value}]'}"
            for param in self.parameters
        ]
        return f"{self.name}: {self.description.rstrip('.')}. Params: ({', '.join(params)})"
