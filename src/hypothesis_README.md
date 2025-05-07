# Hypothesis Operations Module

This module provides CRUD (Create, Read, Update, Delete) operations for Hypothesis nodes in Neo4J. It builds on top of the Neo4JOperations class to provide specialized functionality for handling hypotheses.

## Features

- HypothesisSubject and HypothesisObject dataclasses to represent subject and object data
- A Hypothesis dataclass that uses HypothesisSubject and HypothesisObject instances
- Independent creation, update, and deletion of subject and object nodes
- Reuse of subject and object nodes across multiple hypotheses
- Automatic ID generation for all hypotheses, subjects, and objects
- Create, read, update, and delete Hypothesis nodes in Neo4J
- Find hypotheses by subject name, subject ID, relation, object name, object ID, or confidence range
- Validate hypothesis data (subject, relation, object, confidence)
- Ensure confidence values are between 0 and 1
- Backward compatibility methods for existing code

## Installation

1. Make sure you have Neo4J installed and running.
2. Install the required Python dependencies:

```bash
pip install neo4j python-dotenv
```

## Configuration

The module uses environment variables for Neo4J connection details. Create a `.env` file in your project root with the following variables:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Usage

### Initializing the HypothesisOperations Class

```python
from neo4j_operations import Neo4jOperations
from hypothesis import HypothesisOperations, Hypothesis
from id_provider import UuidProvider
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Initialize the Neo4j operations with a custom ID provider
id_provider = UuidProvider()  # You can use your own implementation of IdProvider
neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, id_provider=id_provider)

# Alternatively, you can use the default ID provider (UuidProvider)
# neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# Initialize the Hypothesis operations
hypothesis_ops = HypothesisOperations(neo4j_ops)
```

For more information about using custom ID providers, see the [Neo4J Operations README](neo4j_operations_README.md#using-a-custom-id-provider).

### Using the HypothesisSubject and HypothesisObject Dataclasses

The module provides two dataclasses for representing subjects and objects:

```python
from hypothesis import HypothesisSubject, HypothesisObject

# Create a subject
earth_subject = HypothesisSubject(
    name="Earth",
    additional_properties={
        "type": "Planet",
        "diameter_km": 12742
    }
)

# Access subject attributes
print(earth_subject.name)  # "Earth"
print(earth_subject.id)  # Auto-generated UUID
print(earth_subject.additional_properties)  # {"type": "Planet", "diameter_km": 12742}

# Create an object
sun_object = HypothesisObject(
    name="Sun",
    additional_properties={
        "type": "Star",
        "diameter_km": 1392700
    }
)

# Access object attributes
print(sun_object.name)  # "Sun"
print(sun_object.id)  # Auto-generated UUID
print(sun_object.additional_properties)  # {"type": "Star", "diameter_km": 1392700}
```

### Using the Hypothesis Dataclass

Every Hypothesis, HypothesisSubject, and HypothesisObject instance will always have a unique ID. If an ID is not explicitly provided when creating these instances, one will be automatically generated. The ID is NEVER optional, ensuring that each instance can be uniquely identified in the system.

```python
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject

# Create subject and object instances
earth_subject = HypothesisSubject(name="Earth")
sun_object = HypothesisObject(name="Sun")

# Create a Hypothesis object using subject and object instances
earth_hypothesis = Hypothesis(
    subject=earth_subject,
    relation="orbits",
    object=sun_object,
    confidence=0.99,
    additional_properties={
        "source": "Astronomical observation",
        "verified": True
    }
)

# Access attributes
print(earth_hypothesis.subject.name)  # "Earth"
print(earth_hypothesis.subject.id)  # Auto-generated UUID
print(earth_hypothesis.relation)  # "orbits"
print(earth_hypothesis.object.name)  # "Sun"
print(earth_hypothesis.object.id)  # Auto-generated UUID
print(earth_hypothesis.confidence)  # 0.99
print(earth_hypothesis.id)  # Auto-generated UUID
print(earth_hypothesis.additional_properties)  # {"source": "Astronomical observation", "verified": True}

# The dataclass validates data on creation
try:
    invalid_subject = HypothesisSubject(name="")  # Invalid: empty name
except ValueError as e:
    print(f"Validation error: {e}")  # "Subject name must be a non-empty string"

try:
    invalid_hypothesis = Hypothesis(
        subject=earth_subject,
        relation="example",
        object=sun_object,
        confidence=1.5  # Invalid: greater than 1
    )
except ValueError as e:
    print(f"Validation error: {e}")  # "Confidence must be between 0 and 1"
```

### Backward Compatibility

For backward compatibility, you can still create a Hypothesis using string values:

```python
# Create a hypothesis using strings (backward compatibility)
earth_hypothesis = Hypothesis.create_from_strings(
    subject="Earth",
    relation="orbits",
    object_="Sun",
    confidence=0.99,
    additional_properties={
        "source": "Astronomical observation",
        "verified": True
    }
)
```

### Creating a Hypothesis

```python
# Create subject and object instances
earth_subject = HypothesisSubject(
    name="Earth",
    additional_properties={"type": "Planet"}
)

sun_object = HypothesisObject(
    name="Sun",
    additional_properties={"type": "Star"}
)

# Create a hypothesis using the subject and object instances
earth_hypothesis = Hypothesis(
    subject=earth_subject,
    relation="orbits",
    object=sun_object,
    confidence=0.99,
    additional_properties={
        "source": "Astronomical observation",
        "verified": True
    }
)

# Save the hypothesis to Neo4J
hypothesis_id = hypothesis_ops.create_hypothesis(earth_hypothesis)
```

### Reading a Hypothesis

```python
# Read a hypothesis by its ID
hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)
# Returns a Hypothesis object or None if not found

# Access the hypothesis attributes
print(hypothesis.subject.name)  # "Earth"
print(hypothesis.subject.id)  # The subject's UUID
print(hypothesis.subject.additional_properties)  # {"type": "Planet"}
print(hypothesis.relation)  # "orbits"
print(hypothesis.object.name)  # "Sun"
print(hypothesis.object.id)  # The object's UUID
print(hypothesis.object.additional_properties)  # {"type": "Star"}
print(hypothesis.confidence)  # 0.99
```

### Updating a Hypothesis

```python
# Get the hypothesis
hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)

# Update subject attributes
hypothesis.subject.name = "Earth (Updated)"
hypothesis.subject.additional_properties["mass_kg"] = 5.97e24

# Update relation
hypothesis.relation = "orbits_around"

# Update object attributes
hypothesis.object.additional_properties["temperature_k"] = 5778

# Update confidence
hypothesis.confidence = 0.999

# Update hypothesis additional properties
hypothesis.additional_properties["last_verified"] = "2023-06-15"

# Save the updates
updated = hypothesis_ops.update_hypothesis(hypothesis)
# Returns True if the hypothesis was updated, False otherwise
```

### Deleting a Hypothesis

```python
# Delete a hypothesis by its ID (also deletes subject and object nodes if not used elsewhere)
deleted = hypothesis_ops.delete_hypothesis(hypothesis_id)
# Returns True if the hypothesis was deleted, False otherwise

# Delete a hypothesis but keep the subject and object nodes
deleted = hypothesis_ops.delete_hypothesis(hypothesis_id, keep_subject_object=True)
# Returns True if the hypothesis was deleted, False otherwise
```

### Finding Hypotheses

```python
# Find hypotheses by subject name
earth_hypotheses = hypothesis_ops.find_hypotheses(subject="Earth")

# Find hypotheses by subject ID
subject_id_hypotheses = hypothesis_ops.find_hypotheses(subject_id=earth_subject.id)

# Find hypotheses by relation
orbit_hypotheses = hypothesis_ops.find_hypotheses(relation="orbits")

# Find hypotheses by object name
sun_hypotheses = hypothesis_ops.find_hypotheses(object_="Sun")

# Find hypotheses by object ID
object_id_hypotheses = hypothesis_ops.find_hypotheses(object_id=sun_object.id)

# Find hypotheses by confidence range
high_confidence = hypothesis_ops.find_hypotheses(min_confidence=0.9)
medium_confidence = hypothesis_ops.find_hypotheses(min_confidence=0.5, max_confidence=0.9)

# Process the results (now Hypothesis objects with HypothesisSubject and HypothesisObject instances)
for h in orbit_hypotheses:
    print(f"{h.subject.name} {h.relation} {h.object.name} (confidence: {h.confidence})")
```

### Backward Compatibility

The module provides backward compatibility methods for existing code:

```python
# Create a hypothesis using individual parameters
hypothesis_id = hypothesis_ops.create_hypothesis_from_params(
    subject="Mars",
    relation="orbits",
    object_="Sun",
    confidence=0.97,
    additional_properties={"note": "Using backward compatibility method"}
)

# Update a hypothesis using individual parameters
hypothesis_ops.update_hypothesis_from_params(
    hypothesis_id=hypothesis_id,
    confidence=0.98,
    additional_properties={"updated": True}
)
```

### Validation

The module validates hypothesis data to ensure:
- Subject, relation, and object are non-empty strings
- Confidence is a number between 0 and 1

If validation fails, a `ValueError` is raised with an appropriate message.

### Closing the Connection

```python
# Always close the connection when done
neo4j_ops.close()
```

## Complete Example

See the `hypothesis_example.py` file for a complete example of how to use all the CRUD operations.

## Data Model

### HypothesisSubject Dataclass

The `HypothesisSubject` dataclass represents the subject of a hypothesis with the following attributes:
- `name`: The name of the subject (string)
- `id`: A unique identifier (auto-generated UUID if not explicitly provided)
- `additional_properties`: A dictionary of any additional properties

The dataclass provides built-in validation to ensure:
- Name is a non-empty string

It also provides methods to convert between the dataclass and dictionaries:
- `to_dict()`: Converts the HypothesisSubject to a dictionary for Neo4j storage
- `from_dict()`: Creates a HypothesisSubject instance from a dictionary (static method)

### HypothesisObject Dataclass

The `HypothesisObject` dataclass represents the object of a hypothesis with the following attributes:
- `name`: The name of the object (string)
- `id`: A unique identifier (auto-generated UUID if not explicitly provided)
- `additional_properties`: A dictionary of any additional properties

The dataclass provides built-in validation to ensure:
- Name is a non-empty string

It also provides methods to convert between the dataclass and dictionaries:
- `to_dict()`: Converts the HypothesisObject to a dictionary for Neo4j storage
- `from_dict()`: Creates a HypothesisObject instance from a dictionary (static method)

### Hypothesis Dataclass

The `Hypothesis` dataclass represents a hypothesis with the following attributes:
- `subject`: The subject of the hypothesis (HypothesisSubject instance)
- `relation`: The relation between subject and object (string)
- `object`: The object of the hypothesis (HypothesisObject instance)
- `confidence`: The confidence level (float between 0 and 1)
- `id`: A unique identifier (auto-generated UUID if not explicitly provided)
- `additional_properties`: A dictionary of any additional properties

Note that the `id` attribute is guaranteed to be set for all Hypothesis, HypothesisSubject, and HypothesisObject instances. If you don't provide an ID when creating these instances, one will be automatically generated during initialization. This ensures that every instance can be uniquely identified in the system.

The dataclass provides built-in validation to ensure:
- Subject is a valid HypothesisSubject instance
- Relation is a non-empty string
- Object is a valid HypothesisObject instance
- Confidence is a number between 0 and 1

It also provides methods to convert between the dataclass and dictionaries:
- `to_dict()`: Converts the Hypothesis to a dictionary for Neo4j storage
- `from_dict()`: Creates a Hypothesis instance from dictionaries (static method)
- `create_from_strings()`: Creates a Hypothesis instance from string values for backward compatibility (static method)

### Neo4J Storage

Each Hypothesis in Neo4J is represented as three connected nodes:

1. **Subject Node**:
   - `id`: A unique identifier (the ID of the HypothesisSubject instance)
   - `nodeType`: Always set to "Subject"
   - `name`: The name of the subject (string)
   - Any additional properties from the HypothesisSubject instance

2. **Relation Node**:
   - `id`: The hypothesis ID (the ID of the Hypothesis instance)
   - `nodeType`: Always set to "Relation"
   - `name`: The relation between subject and object (string)
   - `confidence`: The confidence level (float between 0 and 1)
   - `hypothesisId`: The hypothesis ID (for reference)
   - `subject_id`: The ID of the subject node (for reference)
   - `object_id`: The ID of the object node (for reference)
   - Any additional properties from the Hypothesis instance

3. **Object Node**:
   - `id`: A unique identifier (the ID of the HypothesisObject instance)
   - `nodeType`: Always set to "Object"
   - `name`: The name of the object (string)
   - Any additional properties from the HypothesisObject instance

The nodes are connected with relationships:
- Subject node → Relation node: `FLOWS_TO` relationship
- Relation node → Object node: `FLOWS_TO` relationship

This structure allows for more complex graph queries and better represents the semantic meaning of a hypothesis as a flow from subject through relation to object. It also allows for reusing subject and object nodes across multiple hypotheses, which can be useful for building knowledge graphs.

## Integration with Graph Workflows

The Hypothesis class can be integrated with graph-based workflows to track and manage hypotheses throughout their lifecycle. For example, you can:

1. Create hypotheses based on initial observations
2. Update confidence levels as new evidence is discovered
3. Find related hypotheses to build a knowledge graph
4. Delete invalidated hypotheses when they are disproven
