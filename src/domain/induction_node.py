import uuid
from dataclasses import dataclass, field
from typing import List, Union

from dataclasses_json import dataclass_json

from src.domain.evidence import Evidence
from src.domain.hypothesis import Hypothesis


@dataclass_json
@dataclass(frozen=False, slots=True, order=True)
class InferenceNode:
    node: Union[Hypothesis, Evidence]
    children: list["InferenceNode"] = field(default_factory=list)

    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)

    def __post_init__(self):
        """Validate the inference node data after initialization."""
        if not isinstance(self.node, (Hypothesis, Evidence)):
            raise ValueError("node must be either a Hypothesis or Evidence instance")

        if not isinstance(self.children, list):
            raise ValueError("children must be a list of InferenceNode instances")

        for child in self.children:
            if not isinstance(child, InferenceNode):
                raise ValueError("All children must be InferenceNode instances")

    def __repr__(self) -> str:
        return f"InferenceNode(type={type(self.node)}, content={self.node}, children={str(self.children)})"

    def __str__(self):
        return f"InferenceNode(type={type(self.node)}, content={self.node}, children={str(self.children)})"

    def add_all(self, children):
        self.children += children

    def as_tree(self, level: int = 0) -> str:
        formatted = ""
        spaces = (level - 1) * " "
        formatted += f"{spaces}{'└-' if level > 0 else ""}{self.node.as_tree()}\n"
        for child in self.children:
            formatted += child.as_tree(level + 1)
        return formatted

    def just_str(self):
        return str(self.node)
