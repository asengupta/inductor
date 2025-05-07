# Neo4J Operations Module

This module provides CRUD (Create, Read, Update, Delete) operations for Neo4J nodes. It ensures that each node has an ID and a nodeType property.

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

### Initializing the Neo4jOperations Class

```python
from neo4j_operations import Neo4jOperations
from id_provider import UuidProvider
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Initialize with a custom ID provider
id_provider = UuidProvider()  # You can use your own implementation of IdProvider
neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, id_provider=id_provider)

# Alternatively, you can use the default ID provider (UuidProvider)
# neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
```

### Using a Custom ID Provider

The Neo4jOperations class can be initialized with a custom ID provider that implements the IdProvider interface. This allows you to control how IDs are generated for new nodes.

```python
from id_provider import IdProvider

class CustomIdProvider:
    """A custom implementation of IdProvider."""

    def generate_id(self) -> str:
        """Generate a custom ID."""
        return f"custom-{int(time.time())}"  # Example: time-based ID

# Use the custom ID provider
custom_id_provider = CustomIdProvider()
neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, id_provider=custom_id_provider)
```

### Creating a Node

```python
# Create a node with type, properties, and labels
node_id = neo4j_ops.create_node(
    node_type="Person",  # Required - will be set as nodeType property and used as a label
    properties={
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com"
        # id will be auto-generated if not provided
    },
    labels=["Employee", "Developer"]  # Optional additional labels
)
```

### Reading a Node

```python
# Read a node by its ID
node = neo4j_ops.read_node(node_id)
# Returns a dictionary with all node properties or None if not found
```

### Updating a Node

```python
# Update a node's properties
updated = neo4j_ops.update_node(
    node_id=node_id,
    properties={
        "age": 31,
        "position": "Senior Developer"
    }
)
# Returns True if the node was updated, False otherwise
```

### Deleting a Node

```python
# Delete a node by its ID
deleted = neo4j_ops.delete_node(node_id)
# Returns True if the node was deleted, False otherwise
```

### Finding Nodes

```python
# Find nodes by type, properties, and/or labels
nodes = neo4j_ops.find_nodes(
    node_type="Person",  # Optional
    properties={"age": 31},  # Optional
    labels=["Employee"]  # Optional
)
# Returns a list of dictionaries containing the node properties
```

### Closing the Connection

```python
# Always close the connection when done
neo4j_ops.close()
```

## Complete Example

See the `neo4j_example.py` file for a complete example of how to use all the CRUD operations.

## Notes

- Each node will have an `id` property (auto-generated UUID if not provided) and a `nodeType` property.
- The `nodeType` is also added as a label to the node.
- Additional labels can be provided when creating a node.
- The `id` property cannot be updated.
