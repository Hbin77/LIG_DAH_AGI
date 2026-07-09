from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class AgentTool:
    name: str
    description: str
    handler: Callable[..., Any]

    def run(self, **kwargs: Any) -> Any:
        return self.handler(**kwargs)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, name: str, description: str, handler: Callable[..., Any]) -> None:
        self._tools[name] = AgentTool(name=name, description=description, handler=handler)

    def get(self, name: str) -> AgentTool:
        if name not in self._tools:
            raise KeyError(f"Unknown agent tool: {name}")
        return self._tools[name]

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]
