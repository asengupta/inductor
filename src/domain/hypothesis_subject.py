import uuid
from dataclasses import dataclass, field
from typing import Any

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HypothesisSubject:
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
