from typing import List, TypeVar, Protocol

class BayesNode:
    """
    A node in a Bayesian network that can contain child nodes.

    Attributes:
        alpha (float): A numeric value between 0 and 1
        beta (float): A numeric value between 0 and 1
        children (List[BayesNode]): An ordered list of child BayesNode objects
    """

    def __init__(self, alpha: float = 0.5, beta: float = 0.5, children: list['BayesNode'] = None):
        """
        Initialize a BayesNode with alpha and beta values and optional children.

        Args:
            alpha (float): A numeric value between 0 and 1, defaults to 0.5
            beta (float): A numeric value between 0 and 1, defaults to 0.5
            children (List[BayesNode]): An ordered list of child nodes, defaults to empty list
        """
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")
        if not 0 <= beta <= 1:
            raise ValueError("Beta must be between 0 and 1")

        self.alpha = alpha
        self.beta = beta
        self.children: list[BayesNode] = [] if children is None else children

    def accept(self, visitor: 'BayesNodeVisitor') -> None:
        """
        Accept a visitor and have it visit this node and all child nodes.

        This implements the Visitor pattern, allowing operations on the tree
        without modifying its structure.

        Args:
            visitor (BayesNodeVisitor): The visitor to accept
        """
        visitor.visit(self)
        for child in self.children:
            child.accept(visitor)


# Define a generic type for the visitor result
T = TypeVar('T')

class BayesNodeVisitor(Protocol[T]):
    """
    Visitor pattern protocol for traversing BayesNode trees.

    This protocol follows the visitor pattern to allow operations on BayesNode
    objects without modifying their structure.
    """

    def visit(self, node: BayesNode) -> T:
        """
        Visit a node and return a result.

        Args:
            node (BayesNode): The node to visit

        Returns:
            T: The result of visiting the node
        """
        ...




# Example concrete visitor implementation
class SumAlphaVisitor(BayesNodeVisitor[float]):
    """
    Example visitor that sums the alpha values of all nodes.
    """

    def visit(self, node: BayesNode) -> float:
        """
        Visit a node and return its alpha value.

        Args:
            node (BayesNode): The node to visit

        Returns:
            float: The alpha value of the node
        """
        return node.alpha
