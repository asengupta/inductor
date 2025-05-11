"""
Hypothesis Operations Module

This module provides CRUD operations for Hypothesis nodes in Neo4J.
Each Hypothesis consists of a HypothesisSubject, a relation, a HypothesisObject, and a confidence value.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from dataclasses_json import dataclass_json

from belief import Belief, equally_likely


@dataclass_json
@dataclass
class HypothesisSubject:
    """
    A dataclass representing the subject of a hypothesis.

    Attributes:
        name: The name of the subject
        id: The unique identifier (auto-generated if not explicitly provided)
    """
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate the subject data after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Subject name must be a non-empty string")

    def to_dict(self) -> dict[str, Any]:
        """Convert the subject to a dictionary for Neo4j storage."""
        result = {
            'name': self.name,
            'id': self.id
        }

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'HypothesisSubject':
        """Create a HypothesisSubject instance from a dictionary."""
        if not data:
            raise ValueError("Cannot create HypothesisSubject from empty data")

        # Extract the main attributes
        name = data.get('name', '')
        id_ = data.get('id', str(uuid.uuid4()))

        return cls(
            name=name,
            id=id_
        )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


@dataclass_json
@dataclass
class HypothesisObject:
    """
    A dataclass representing the object of a hypothesis.

    Attributes:
        name: The name of the object
        id: The unique identifier (auto-generated if not explicitly provided)
    """
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate the object data after initialization."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Object name must be a non-empty string")

    def to_dict(self) -> dict[str, Any]:
        """Convert the object to a dictionary for Neo4j storage."""
        result = {
            'name': self.name,
            'id': self.id
        }

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'HypothesisObject':
        """Create a HypothesisObject instance from a dictionary."""
        if not data:
            raise ValueError("Cannot create HypothesisObject from empty data")

        # Extract the main attributes
        name = data.get('name', '')
        id_ = data.get('id', str(uuid.uuid4()))

        return cls(
            name=name,
            id=id_
        )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


@dataclass_json
@dataclass
class Hypothesis:
    subject: HypothesisSubject
    relation: str
    object: HypothesisObject
    belief: Belief = field(default_factory=equally_likely)
    contribution_to_root: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __repr__(self):
        return f"{self.subject} {self.relation} {self.object} with a belief of {self.belief}."

    def __str__(self):
        return f"{self.subject} {self.relation} {self.object} with a belief of {self.belief}."

    def as_tree(self) -> str:
        return f"[HYPOTHESIS] {self.subject} {self.relation} {self.object}"

    def __post_init__(self):
        if not isinstance(self.subject, HypothesisSubject):
            raise ValueError("Subject must be a HypothesisSubject instance")

        if not self.relation or not isinstance(self.relation, str):
            raise ValueError("Relation must be a non-empty string")

        if not isinstance(self.object, HypothesisObject):
            raise ValueError("Object must be a HypothesisObject instance")

        if not isinstance(self.belief, Belief):
            raise ValueError("Belief must be a Belief instance")

        if not isinstance(self.contribution_to_root, (int, float)):
            raise ValueError("contribution_to_root must be a number")

        if self.contribution_to_root < 0 or self.contribution_to_root > 1:
            raise ValueError("contribution_to_root must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        result = {
            'subject': self.subject.name,  # For backward compatibility
            'relation': self.relation,
            'object': self.object.name,  # For backward compatibility
            'belief': self.belief.to_dict(),
            'contribution_to_root': self.contribution_to_root,
            'id': self.id,  # Always include the ID
            'subject_id': self.subject.id,
            'object_id': self.object.id
        }

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any], subject_data: dict[str, Any] = None,
                  object_data: dict[str, Any] = None) -> 'Hypothesis':
        if not data:
            raise ValueError("Cannot create Hypothesis from empty data")

        # Extract the main attributes
        relation = data.get('relation', '')
        belief_data = data.get('belief', None)
        belief = Belief.from_dict(belief_data) if belief_data else equally_likely()
        contribution_to_root = data.get('contribution_to_root', 0.0)
        id_ = data.get('id', str(uuid.uuid4()))

        # Create subject
        if subject_data:
            subject = HypothesisSubject.from_dict(subject_data)
        else:
            # For backward compatibility
            subject = HypothesisSubject(
                name=data.get('subject', ''),
                id=data.get('subject_id', str(uuid.uuid4()))
            )

        # Create object
        if object_data:
            object_ = HypothesisObject.from_dict(object_data)
        else:
            # For backward compatibility
            object_ = HypothesisObject(
                name=data.get('object', ''),
                id=data.get('object_id', str(uuid.uuid4()))
            )

        return cls(
            subject=subject,
            relation=relation,
            object=object_,
            belief=belief,
            contribution_to_root=contribution_to_root,
            id=id_
        )

    @classmethod
    def create_from_strings(cls, subject: str, relation: str, object_: str,
                            belief: Belief = None, contribution_to_root: float = 0.0,
                            id_: str = None) -> 'Hypothesis':
        if id_ is None:
            id_ = str(uuid.uuid4())

        if belief is None:
            belief = equally_likely()

        subject_obj = HypothesisSubject(name=subject)
        object_obj = HypothesisObject(name=object_)

        return cls(
            subject=subject_obj,
            relation=relation,
            object=object_obj,
            belief=belief,
            contribution_to_root=contribution_to_root,
            id=id_
        )
