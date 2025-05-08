from graph.nodes.bayes_node import BayesNode, BayesNodeVisitor

def test_bayes_node_creation():
    """Test creating BayesNode objects with valid and invalid values."""
    # Valid values
    node1 = BayesNode(0.3, 0.7)
    assert node1.alpha == 0.3
    assert node1.beta == 0.7

    # Default values
    node2 = BayesNode()
    assert node2.alpha == 0.5
    assert node2.beta == 0.5

    # Test boundary values
    node3 = BayesNode(0.0, 1.0)
    assert node3.alpha == 0.0
    assert node3.beta == 1.0

    # Invalid values should raise ValueError
    try:
        BayesNode(-0.1, 0.5)
        assert False, "Should have raised ValueError for alpha < 0"
    except ValueError:
        pass

    try:
        BayesNode(0.5, 1.1)
        assert False, "Should have raised ValueError for beta > 1"
    except ValueError:
        pass

def test_bayes_node_tree():
    """Test building a tree of BayesNode objects."""
    # Create nodes with children in the constructor
    grandchild1 = BayesNode(0.4, 0.6)
    grandchild2 = BayesNode(0.5, 0.5)
    child1 = BayesNode(0.2, 0.8, [grandchild1])
    child2 = BayesNode(0.3, 0.7, [grandchild2])
    root = BayesNode(0.1, 0.9, [child1, child2])

    # Verify tree structure
    assert len(root.children) == 2
    assert root.children[0] == child1
    assert root.children[1] == child2
    assert len(child1.children) == 1
    assert child1.children[0] == grandchild1
    assert len(child2.children) == 1
    assert child2.children[0] == grandchild2

class ResultCollectorVisitor(BayesNodeVisitor[None]):
    """Visitor that collects values from nodes in a list."""
    def __init__(self, value_extractor):
        """
        Initialize with a function that extracts a value from a node.

        Args:
            value_extractor: A function that takes a BayesNode and returns a value
        """
        self.results = []
        self.value_extractor = value_extractor

    def visit(self, node: BayesNode) -> None:
        """
        Visit a node and collect its value.

        Args:
            node (BayesNode): The node to visit
        """
        self.results.append(self.value_extractor(node))

def test_visitor_pattern():
    """Test the visitor pattern implementation."""
    # Create a tree using the constructor with children
    grandchild1 = BayesNode(0.4, 0.6)
    child1 = BayesNode(0.2, 0.8, [grandchild1])
    child2 = BayesNode(0.3, 0.7)
    root = BayesNode(0.1, 0.9, [child1, child2])

    # Test visitor that collects alpha values
    alpha_visitor = ResultCollectorVisitor(lambda node: node.alpha)
    root.accept(alpha_visitor)

    # Should have collected 4 alpha values
    assert len(alpha_visitor.results) == 4

    # Sum of all alphas should be the same as before
    assert sum(alpha_visitor.results) == 0.1 + 0.2 + 0.3 + 0.4

    # Test visitor that counts nodes
    count_visitor = ResultCollectorVisitor(lambda node: 1)
    root.accept(count_visitor)

    # Should have counted 4 nodes
    assert sum(count_visitor.results) == 4

if __name__ == "__main__":
    print("Running BayesNode tests...")
    test_bayes_node_creation()
    test_bayes_node_tree()
    test_visitor_pattern()
    print("All tests passed!")
