"""
Test script for the Evidence class.
"""

from evidence import Evidence

def test_evidence_creation():
    """Test creating an Evidence instance."""
    # Create an Evidence instance
    evidence = Evidence(
        evidence_description="Test evidence",
        contribution_to_hypothesis=0.5
    )

    # Check that the attributes are set correctly
    assert evidence.evidence_description == "Test evidence"
    assert evidence.contribution_to_hypothesis == 0.5
    assert evidence.id is not None

def test_evidence_immutability():
    """Test that Evidence instances are immutable."""
    evidence = Evidence(
        evidence_description="Test evidence",
        contribution_to_hypothesis=0.5
    )

    try:
        evidence.evidence_description = "Modified evidence"
        assert False, "Should not be able to modify frozen dataclass"
    except AttributeError:
        pass

def test_evidence_comparison():
    """Test that Evidence instances can be compared."""
    evidence1 = Evidence(
        evidence_description="Test evidence 1",
        contribution_to_hypothesis=0.5
    )

    evidence2 = Evidence(
        evidence_description="Test evidence 2",
        contribution_to_hypothesis=0.5
    )

    evidence3 = Evidence(
        evidence_description="Test evidence 1",
        contribution_to_hypothesis=0.7
    )

    # Same description, different contribution - evidence3 should be greater
    assert evidence3 > evidence1

    # Different description, same contribution - evidence2 should be greater (alphabetical order)
    assert evidence2 > evidence1

def test_evidence_validation():
    """Test that Evidence validates contribution_to_hypothesis."""
    try:
        Evidence(
            evidence_description="Test evidence",
            contribution_to_hypothesis=1.5
        )
        assert False, "Should raise ValueError for contribution > 1"
    except ValueError:
        pass

    try:
        Evidence(
            evidence_description="Test evidence",
            contribution_to_hypothesis=-0.5
        )
        assert False, "Should raise ValueError for contribution < 0"
    except ValueError:
        pass

    try:
        Evidence(
            evidence_description="Test evidence",
            contribution_to_hypothesis="not a number"
        )
        assert False, "Should raise ValueError for non-numeric contribution"
    except ValueError:
        pass

def test_evidence_repr():
    """Test the string representation of Evidence."""
    evidence = Evidence(
        evidence_description="Test evidence",
        contribution_to_hypothesis=0.5
    )

    repr_str = repr(evidence)
    assert "description='Test evidence'" in repr_str
    assert "contribution=0.5" in repr_str
    assert "id='" in repr_str

if __name__ == "__main__":
    test_evidence_creation()
    test_evidence_immutability()
    test_evidence_comparison()
    test_evidence_validation()
    test_evidence_repr()
    print("All tests passed!")
