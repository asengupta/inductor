import uuid
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True, slots=True, order=True)
class Belief:
    alpha: int
    beta: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)

    def __repr__(self) -> str:
        return f"Belief(alpha='{self.alpha}', beta={self.beta}, id='{self.id}')"

    def as_tree(self) -> str:
        return f"Belief(alpha='{self.alpha}', beta={self.beta}, id='{self.id}')"

def no_evidence():
    return Belief(0, 0)

def equally_likely():
    return Belief(1, 1)
