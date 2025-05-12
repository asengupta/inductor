import uuid
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from beta_bernoulli_belief import BetaBernoulliBelief, random_belief
from random_words import random_text


@dataclass_json
@dataclass(frozen=False, slots=True, order=True)
class Evidence:
    evidence_description: str
    contribution_to_hypothesis: float
    belief: BetaBernoulliBelief
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)

    def __post_init__(self):
        if not isinstance(self.contribution_to_hypothesis, (int, float)):
            raise ValueError("contribution_to_hypothesis must be a number")

        if self.contribution_to_hypothesis < 0 or self.contribution_to_hypothesis > 1:
            raise ValueError("contribution_to_hypothesis must be between 0 and 1")

    def __repr__(self) -> str:
        return f"Evidence(description='{self.evidence_description}', contribution={self.contribution_to_hypothesis}, id='{self.id}, belief={self.belief})')"

    def as_tree(self) -> str:
        return f"[EVIDENCE] ({self.belief}) {self.evidence_description}"


def random_evidence() -> Evidence:
    return Evidence(random_text(), 0.4, random_belief())
