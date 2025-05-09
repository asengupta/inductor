"""
Test script for the Hypothesis class.
"""

from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject

def test_hypothesis_creation():
    """Test creating a Hypothesis instance with contribution_to_root."""
    # Create a Hypothesis instance
    subject = HypothesisSubject(name="Test Subject")
    object_ = HypothesisObject(name="Test Object")
    hypothesis = Hypothesis(
        subject=subject,
        relation="Test Relation",
        object=object_,
        confidence=0.8,
        contribution_to_root=0.5
    )

    # Check that the attributes are set correctly
    assert hypothesis.subject.name == "Test Subject"
    assert hypothesis.relation == "Test Relation"
    assert hypothesis.object.name == "Test Object"
    assert hypothesis.confidence == 0.8
    assert hypothesis.contribution_to_root == 0.5
    assert hypothesis.id is not None

def test_hypothesis_validation():
    """Test that Hypothesis validates contribution_to_root."""
    subject = HypothesisSubject(name="Test Subject")
    object_ = HypothesisObject(name="Test Object")

    try:
        Hypothesis(
            subject=subject,
            relation="Test Relation",
            object=object_,
            confidence=0.8,
            contribution_to_root=1.5
        )
        assert False, "Should raise ValueError for contribution_to_root > 1"
    except ValueError as e:
        assert "contribution_to_root must be between 0 and 1" in str(e)

    try:
        Hypothesis(
            subject=subject,
            relation="Test Relation",
            object=object_,
            confidence=0.8,
            contribution_to_root=-0.5
        )
        assert False, "Should raise ValueError for contribution_to_root < 0"
    except ValueError as e:
        assert "contribution_to_root must be between 0 and 1" in str(e)

    try:
        Hypothesis(
            subject=subject,
            relation="Test Relation",
            object=object_,
            confidence=0.8,
            contribution_to_root="not a number"
        )
        assert False, "Should raise ValueError for non-numeric contribution_to_root"
    except ValueError as e:
        assert "contribution_to_root must be a number" in str(e)

def test_hypothesis_to_dict():
    """Test converting a Hypothesis to a dictionary."""
    subject = HypothesisSubject(name="Test Subject")
    object_ = HypothesisObject(name="Test Object")
    hypothesis = Hypothesis(
        subject=subject,
        relation="Test Relation",
        object=object_,
        confidence=0.8,
        contribution_to_root=0.5
    )

    # Convert to dictionary
    dict_data = hypothesis.to_dict()

    # Check that the dictionary contains the expected keys and values
    assert dict_data['subject'] == "Test Subject"
    assert dict_data['relation'] == "Test Relation"
    assert dict_data['object'] == "Test Object"
    assert dict_data['confidence'] == 0.8
    assert dict_data['contribution_to_root'] == 0.5
    assert 'id' in dict_data
    assert 'subject_id' in dict_data
    assert 'object_id' in dict_data

def test_hypothesis_from_dict():
    """Test creating a Hypothesis from a dictionary."""
    # Create a dictionary
    dict_data = {
        'subject': "Test Subject",
        'relation': "Test Relation",
        'object': "Test Object",
        'confidence': 0.8,
        'contribution_to_root': 0.5,
        'id': "test-id",
        'subject_id': "subject-id",
        'object_id': "object-id"
    }

    # Create a Hypothesis from the dictionary
    hypothesis = Hypothesis.from_dict(dict_data)

    # Check that the attributes are set correctly
    assert hypothesis.subject.name == "Test Subject"
    assert hypothesis.relation == "Test Relation"
    assert hypothesis.object.name == "Test Object"
    assert hypothesis.confidence == 0.8
    assert hypothesis.contribution_to_root == 0.5
    assert hypothesis.id == "test-id"

def test_hypothesis_create_from_strings():
    """Test creating a Hypothesis using create_from_strings."""
    # Create a Hypothesis using create_from_strings
    hypothesis = Hypothesis.create_from_strings(
        subject="Test Subject",
        relation="Test Relation",
        object_="Test Object",
        confidence=0.8,
        contribution_to_root=0.5
    )

    # Check that the attributes are set correctly
    assert hypothesis.subject.name == "Test Subject"
    assert hypothesis.relation == "Test Relation"
    assert hypothesis.object.name == "Test Object"
    assert hypothesis.confidence == 0.8
    assert hypothesis.contribution_to_root == 0.5
    assert hypothesis.id is not None

if __name__ == "__main__":
    test_hypothesis_creation()
    test_hypothesis_validation()
    test_hypothesis_to_dict()
    test_hypothesis_from_dict()
    test_hypothesis_create_from_strings()
    print("All tests passed!")
