import uuid
from dataclasses import dataclass, field
from typing import List, Union

from dataclasses_json import dataclass_json

from evidence import Evidence
from hypothesis import Hypothesis


@dataclass_json
@dataclass(frozen=False, slots=True, order=True)
class InferenceNode:
    node: Union[Hypothesis, Evidence]
    children: List["InferenceNode"] = field(default_factory=list)

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
