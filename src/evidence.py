"""
Evidence Module

This module provides the Evidence class which represents evidence that contributes to a hypothesis.
Each Evidence consists of a description, a contribution value to the hypothesis, and a unique identifier.
"""

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, order=True)
class Evidence:
    """
    A class representing evidence that contributes to a hypothesis.

    Attributes:
        evidence_description (str): A description of the evidence.
        contribution_to_hypothesis (float): A value between 0 and 1 representing how much this
                                           evidence contributes to the hypothesis.
        id (str): A unique identifier for this evidence, defaults to a UUID.
    """
    evidence_description: str
    contribution_to_hypothesis: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)

    def __post_init__(self):
        if not isinstance(self.contribution_to_hypothesis, (int, float)):
            raise ValueError("contribution_to_hypothesis must be a number")

        if self.contribution_to_hypothesis < 0 or self.contribution_to_hypothesis > 1:
            raise ValueError("contribution_to_hypothesis must be between 0 and 1")

    def __repr__(self) -> str:
        """Return a string representation of the Evidence."""
        return f"Evidence(description='{self.evidence_description}', contribution={self.contribution_to_hypothesis}, id='{self.id}')"
