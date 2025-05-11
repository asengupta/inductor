import uuid
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True, slots=True, order=True)
class Evidence:
    evidence_description: str
    contribution_to_hypothesis: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)

    def __post_init__(self):
        if not isinstance(self.contribution_to_hypothesis, (int, float)):
            raise ValueError("contribution_to_hypothesis must be a number")

        if self.contribution_to_hypothesis < 0 or self.contribution_to_hypothesis > 1:
            raise ValueError("contribution_to_hypothesis must be between 0 and 1")

    def __repr__(self) -> str:
        return f"Evidence(description='{self.evidence_description}', contribution={self.contribution_to_hypothesis}, id='{self.id}')"

    def as_tree(self) -> str:
        return f"[EVIDENCE] {self.evidence_description}"
