import random
import uuid
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from belief import BeliefProtocol


@dataclass_json
@dataclass(frozen=True, slots=True, order=True)
class BetaBernoulliBelief(BeliefProtocol):
    alpha: int
    beta: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)

    def __repr__(self) -> str:
        return f"({self.alpha}, {self.beta})"

    def __str__(self) -> str:
        return f"({self.alpha}, {self.beta})"

    def update(self, data: tuple[int, int]) -> "BetaBernoulliBelief":
        """Update the belief with new evidence."""
        return BetaBernoulliBelief(
            alpha=self.alpha + data[0],
            beta=self.beta + data[1]
        )

    def mean(self) -> float:
        """Return the mean of the belief distribution."""
        if self.alpha + self.beta == 0:
            return 0.5  # Default to 0.5 when no evidence
        return self.alpha / (self.alpha + self.beta)

    def sample(self) -> float:
        """Return a random sample from the belief distribution."""
        if self.alpha + self.beta == 0:
            return random.random()  # Uniform distribution when no evidence
        return random.betavariate(self.alpha + 1, self.beta + 1)


def no_evidence():
    return BetaBernoulliBelief(0, 0)


def equally_likely():
    return BetaBernoulliBelief(1, 1)


def random_belief():
    return BetaBernoulliBelief(1, 1)
