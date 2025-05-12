from typing import List, TypeVar, Protocol

class BayesNode:
    def __init__(self, alpha: float = 0.5, beta: float = 0.5, children: list['BayesNode'] = None):
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")
        if not 0 <= beta <= 1:
            raise ValueError("Beta must be between 0 and 1")

        self.alpha = alpha
        self.beta = beta
        self.children: list[BayesNode] = [] if children is None else children

    def accept(self, visitor: 'BayesNodeVisitor') -> None:
        visitor.visit(self)
        for child in self.children:
            child.accept(visitor)


# Define a generic type for the visitor result
T = TypeVar('T')

class BayesNodeVisitor(Protocol[T]):
    def visit(self, node: BayesNode) -> T:
        ...




# Example concrete visitor implementation
class SumAlphaVisitor(BayesNodeVisitor[float]):
    def visit(self, node: BayesNode) -> float:
        return node.alpha
