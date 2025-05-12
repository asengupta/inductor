from typing import Protocol, Self, runtime_checkable


@runtime_checkable
class BeliefProtocol(Protocol):
    def update(self, data: tuple[int, int]) -> Self:
        """Update the belief with new evidence."""
        ...

    def mean(self) -> float:
        """Return the mean of the belief distribution."""
        ...

    def sample(self) -> float:
        """Return a random sample from the belief distribution."""
        ...
