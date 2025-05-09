"""
Hypothesis Operations Module

This module provides CRUD operations for Hypothesis nodes in Neo4J.
Each Hypothesis consists of a HypothesisSubject, a relation, a HypothesisObject, and a confidence value.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any


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

    def to_dict(self) -> Dict[str, Any]:
        """Convert the subject to a dictionary for Neo4j storage."""
        result = {
            'name': self.name,
            'id': self.id
        }

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HypothesisSubject':
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for Neo4j storage."""
        result = {
            'name': self.name,
            'id': self.id
        }

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HypothesisObject':
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


@dataclass
class Hypothesis:
    """
    A dataclass representing a hypothesis with subject, relation, object, confidence, and contribution to root.

    Attributes:
        subject: The subject of the hypothesis (HypothesisSubject)
        relation: The relation between subject and object (string)
        object: The object of the hypothesis (HypothesisObject)
        confidence: The confidence level (between 0 and 1)
        contribution_to_root: How much this hypothesis contributes to the root hypothesis (between 0 and 1)
        id: The unique identifier (auto-generated if not explicitly provided)
    """
    subject: HypothesisSubject
    relation: str
    object: HypothesisObject
    confidence: float
    contribution_to_root: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate the hypothesis data after initialization."""
        if not isinstance(self.subject, HypothesisSubject):
            raise ValueError("Subject must be a HypothesisSubject instance")

        if not self.relation or not isinstance(self.relation, str):
            raise ValueError("Relation must be a non-empty string")

        if not isinstance(self.object, HypothesisObject):
            raise ValueError("Object must be a HypothesisObject instance")

        if not isinstance(self.confidence, (int, float)):
            raise ValueError("Confidence must be a number")

        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("Confidence must be between 0 and 1")

        if not isinstance(self.contribution_to_root, (int, float)):
            raise ValueError("contribution_to_root must be a number")

        if self.contribution_to_root < 0 or self.contribution_to_root > 1:
            raise ValueError("contribution_to_root must be between 0 and 1")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the hypothesis to a dictionary for Neo4j storage."""
        result = {
            'subject': self.subject.name,  # For backward compatibility
            'relation': self.relation,
            'object': self.object.name,  # For backward compatibility
            'confidence': self.confidence,
            'contribution_to_root': self.contribution_to_root,
            'id': self.id,  # Always include the ID
            'subject_id': self.subject.id,
            'object_id': self.object.id
        }

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any], subject_data: Dict[str, Any] = None,
                  object_data: Dict[str, Any] = None) -> 'Hypothesis':
        """
        Create a Hypothesis instance from dictionaries.

        Args:
            data: Dictionary containing hypothesis data
            subject_data: Dictionary containing subject data (optional)
            object_data: Dictionary containing object data (optional)

        Returns:
            A Hypothesis instance
        """
        if not data:
            raise ValueError("Cannot create Hypothesis from empty data")

        # Extract the main attributes
        relation = data.get('relation', '')
        confidence = data.get('confidence', 0.0)
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
            confidence=confidence,
            contribution_to_root=contribution_to_root,
            id=id_
        )

    @classmethod
    def create_from_strings(cls, subject: str, relation: str, object_: str,
                            confidence: float, contribution_to_root: float = 0.0,
                            id_: str = None) -> 'Hypothesis':
        """
        Create a Hypothesis instance from string values for backward compatibility.

        Args:
            subject: The subject name
            relation: The relation
            object_: The object name
            confidence: The confidence level
            contribution_to_root: How much this hypothesis contributes to the root hypothesis (between 0 and 1)
            id_: The hypothesis ID (optional)

        Returns:
            A Hypothesis instance
        """
        if id_ is None:
            id_ = str(uuid.uuid4())

        subject_obj = HypothesisSubject(name=subject)
        object_obj = HypothesisObject(name=object_)

        return cls(
            subject=subject_obj,
            relation=relation,
            object=object_obj,
            confidence=confidence,
            contribution_to_root=contribution_to_root,
            id=id_
        )
